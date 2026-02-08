# =============================================================================
# ampcompiler.py
#
# Copyright (C) 2023 B. Wang
# All rights reserved.
# Licensed under the BSD open source license agreement
#
# Compiler for AmpScript AST to JavaScript and Python targets.
# =============================================================================
"""Compilers to translate AmpScript AST to JavaScript and Python."""

import logging
from . import ampyacc

logger = logging.getLogger(__name__)


class AmpCompiler:
    """Base class for AmpScript compilers."""

    def __init__(self, tree):
        """
        Initialize the compiler with an AST.

        Args:
            tree: Parsed AST from ampyacc.parse()
        """
        self.tree = tree
        self.output = ""

    def walk_tree(self, tree):
        """
        Recursively walk the AST tree and evaluate nodes.

        Args:
            tree: AST node (tuple or leaf)
        """
        if isinstance(tree, tuple):
            if isinstance(tree[0], tuple):
                self.walk_tree(tree[0])  # Process head
                self.walk_tree(tree[1])  # Process tail
            self.eval(tree)

    def flatten_list(self, nested_list, flattened=None):
        """
        Flatten a nested list structure from the AST.

        Args:
            nested_list: Nested list of tuples
            flattened: Accumulator list (default: new list)

        Returns:
            Flattened list
        """
        if flattened is None:
            flattened = []
        for item in nested_list:
            if isinstance(item, tuple):
                self.flatten_list(item, flattened)
            else:
                flattened.append(item)
        return flattened

    def convert_value_to_string(self, value_tuple):
        """
        Convert an AST value tuple to a string representation.

        Args:
            value_tuple: Tuple like ('INT', 42) or ('STR', 'hello')

        Returns:
            String representation for target language
        """
        raise NotImplementedError("Subclasses must implement this method")

    def releval(self, element):
        """Evaluate a relational expression."""
        raise NotImplementedError("Subclasses must implement this method")

    def loop(self, element, output_str=""):
        """Process loop/conditional body statements."""
        raise NotImplementedError("Subclasses must implement this method")

    def eval(self, element):
        """Evaluate an AST element."""
        raise NotImplementedError("Subclasses must implement this method")


class AmpCompilerToPy(AmpCompiler):
    """Compiler to translate AmpScript AST to Python code."""

    def __init__(self, tree):
        """Initialize Python compiler with AST."""
        super().__init__(tree)
        self.indent_level = 0
        self.indent_str = "    "  # 4 spaces

    def compile(self):
        """Compile the AST to Python code and print output."""
        self.output += "from src import ampfunctions\n"
        self.walk_tree(self.tree)
        print(self.output)

    def get_indent(self):
        """Get current indentation string."""
        return self.indent_str * self.indent_level

    def convert_value_to_string(self, value_tuple):
        """Convert value tuple to Python expression string."""
        if value_tuple[0] == 'INT':
            return f"{value_tuple[1]}"
        elif value_tuple[0] == 'STR':
            return f"'{value_tuple[1]}'"
        elif value_tuple[0] == '@':
            return f"{value_tuple[1]}_amp"
        elif value_tuple[0] in ('BINOP', 'RELOP', 'UNARY', 'GROUP'):
            return self.releval(value_tuple)
        return ""

    def releval(self, element):
        """Evaluate relational expression to Python code."""
        if isinstance(element[0], tuple):
            self.loop(element[0])
            self.loop(element[1])
        else:
            op = element[0]
            if op == 'GROUP':
                return f"({self.releval(element[1])})"
            elif op in ('RELOP', 'BINOP'):
                operator = element[1]
                # Convert JavaScript operators to Python
                if operator == '&&':
                    operator = 'and'
                elif operator == '||':
                    operator = 'or'
                elif operator == '===':
                    operator = '=='
                elif operator == '!==':
                    operator = '!='
                else:
                    operator = operator.lower()
                return f"{self.releval(element[2])} {operator} {self.releval(element[3])}"
            elif op == 'UNARY':
                unary_op = element[1]
                if unary_op == '!':
                    return f"not {self.releval(element[2])}"
                else:
                    return f"{unary_op}{self.releval(element[2])}"
            elif op == '@':
                return f"{element[1]}_amp"
            elif op == 'INT':
                return str(element[1])
            elif op == 'STR':
                return f"'{element[1]}'"
        return ""

    def loop(self, element, output_str=""):
        """Process loop body statements for Python."""
        if isinstance(element[0], tuple):
            output_str += self.loop(element[0])
            output_str += self.loop(element[1])
        else:
            op = element[0]
            if op == 'ELSEIF':
                output_str += f"{self.get_indent()}elif {self.releval(element[1])}: \n"
                self.indent_level += 1
                output_str += self.loop(element[2])
                self.indent_level -= 1
            elif op == 'FUNC':
                output_str = f"{self.get_indent()}getattr(ampfunctions,'{element[1]}')({self.convert_value_to_string(element[2])})\n"
            else:
                # Handle any other statement type (IF, SET, VAR, FOR, etc.)
                saved_output = self.output
                self.output = ""
                self.eval(element)
                # Add indentation only to lines that don't already have leading spaces
                lines = self.output.split('\n')
                for line in lines:
                    if line.strip():
                        if line.lstrip() == line:
                            output_str += self.get_indent() + line + '\n'
                        else:
                            output_str += line + '\n'
                    elif line:
                        output_str += '\n'
                self.output = saved_output
        return output_str

    def eval(self, element):
        """Evaluate an AST element to Python code."""
        op = element[0]

        if op == 'JSBLOCK':
            # JavaScript block wrapper
            self.walk_tree(element[1])
        elif op == 'TRYCATCH':
            # Try-catch block
            self.output += "try:\n"
            self.output += self.loop(element[1])
            self.output += "except Exception"
            if element[2]:  # Exception variable name
                self.output += f" as {element[2]}"
            self.output += ":\n"
            self.output += self.loop(element[3])
        elif op == 'JSVAR':
            # JavaScript variable declaration (var, let, const)
            var_name = element[2]
            var_value = element[3]
            if var_value:
                self.output += f"{var_name} = {self.convert_value_to_string(var_value)}\n"
            else:
                self.output += f"{var_name} = None\n"
        elif op == 'JSFUNC':
            # JavaScript function
            func_name = element[1]
            func_body = element[2]
            self.output += f"def {func_name}():\n"
            self.output += self.loop(func_body)
        elif op == 'JSIF':
            # JavaScript if statement
            self.output += f"if {self.releval(element[1])}:\n"
            self.output += self.loop(element[2])
        elif op == 'JSIFELSE':
            # JavaScript if-else statement
            self.output += f"if {self.releval(element[1])}:\n"
            self.output += self.loop(element[2])
            self.output += "else:\n"
            self.output += self.loop(element[3])
        elif op == 'JSWHILE':
            # JavaScript while loop
            self.output += f"while {self.releval(element[1])}:\n"
            self.output += self.loop(element[2])
        elif op == 'JSFOR':
            # JavaScript for loop
            var_name = element[1]
            init_val = element[2]
            condition = element[3]
            body = element[4]
            self.output += f"{var_name} = {self.convert_value_to_string(init_val)}\n"
            self.output += f"while {self.releval(condition)}:\n"
            self.indent_level += 1
            self.output += self.loop(body)
            self.output += f"{self.get_indent()}{var_name} += 1\n"
            self.indent_level -= 1
        elif op == 'AMPSCRIPT':
            # Embedded AmpScript within JavaScript
            self.walk_tree(element[1])
        elif op == 'VAR':
            if isinstance(element[1], tuple):
                flattened = self.flatten_list(element[1])
                for var in flattened:
                    if var != '@':
                        self.output += f"{var}_amp = None\n"
            else:
                self.output += f"{element[2]}_amp = None\n"
        elif op == 'SET':
            self.output += f"{element[1]}_amp = {self.convert_value_to_string(element[2])}\n"
        elif op == 'IF':
            self.output += f"if {self.releval(element[1])}: \n"
            self.indent_level += 1
            self.output += f"{self.loop(element[2])}"
            self.indent_level -= 1
        elif op == 'IFELSE':
            self.output += f"if {self.releval(element[1])}: \n"
            self.indent_level += 1
            self.output += f"{self.loop(element[2])}"
            self.indent_level -= 1
            # Check if element[3] is an ELSEIFCHAIN or just statements
            if isinstance(element[3], tuple) and element[3][0] == 'ELSEIFCHAIN':
                self.output += f"{self.loop(element[3][1])}"  # Process elseif chain
                self.output += f"else: \n"
                self.indent_level += 1
                self.output += f"{self.loop(element[3][2])}"  # Final else block
                self.indent_level -= 1
            else:
                self.output += f"else: \n"
                self.indent_level += 1
                self.output += f"{self.loop(element[3])}"
                self.indent_level -= 1
        elif op == 'ELSEIF':
            # Handle chained ELSEIFs
            if len(element) == 4:
                # Single ELSEIF: ('ELSEIF', condition, statements)
                self.output += f"elif {self.releval(element[1])}: \n"
                self.indent_level += 1
                self.output += f"{self.loop(element[2])}"
                self.indent_level -= 1
            else:
                # Chained: ('ELSEIF', previous_chain, condition, statements)
                self.output += f"{self.loop(element[1])}"  # Process previous chain
                self.output += f"elif {self.releval(element[2])}: \n"
                self.indent_level += 1
                self.output += f"{self.loop(element[3])}"
                self.indent_level -= 1
        elif op == 'FOR':
            loopvar = element[1]
            initval = element[2]
            finval = element[4]
            stepval = element[5]
            direction = element[3]

            self.output += f"{loopvar}_amp = {self.convert_value_to_string(initval)}\n"
            self.output += f"while {loopvar}_amp < {self.convert_value_to_string(finval)}: \n"
            self.indent_level += 1
            self.output += f"{self.loop(stepval)}"
            self.output += f"{self.get_indent()}{loopvar}_amp += 1\n" if direction == 'TO' else f"{self.get_indent()}{loopvar}_amp -= 1\n"
            self.indent_level -= 1
        elif op == '@':
            self.output += f"{element[1]}_amp = None\n"
        elif op == 'FUNC':
            func_call = f"getattr(ampfunctions,'{element[1]}')({self.convert_value_to_string(element[2])})\n"
            self.output += func_call


class AmpCompilerToJs(AmpCompiler):
    """Compiler to translate AmpScript AST to JavaScript code."""

    def __init__(self, tree):
        """Initialize JavaScript compiler with AST."""
        super().__init__(tree)

    def compile(self):
        """Compile the AST to JavaScript code and print output."""
        self.walk_tree(self.tree)
        print(self.output)

    def convert_value_to_string(self, value_tuple):
        """Convert value tuple to JavaScript expression string."""
        if value_tuple[0] == 'INT':
            return f"{value_tuple[1]}"
        elif value_tuple[0] == 'STR':
            return f"'{value_tuple[1]}'"
        elif value_tuple[0] == '@':
            return f"{value_tuple[1]}"
        return ""

    def releval(self, element):
        """Evaluate relational expression to JavaScript code."""
        if isinstance(element[0], tuple):
            self.loop(element[0])
            self.loop(element[1])
        else:
            op = element[0]
            if op == 'GROUP':
                return f"({self.releval(element[1])})"
            elif op in ('RELOP', 'BINOP'):
                sign = ''
                if element[1].lower() == 'and':
                    sign = '&&'
                elif element[1].lower() == 'or':
                    sign = '||'
                else:
                    sign = element[1].lower()
                return f"{self.releval(element[2])} {sign} {self.releval(element[3])}"
            elif op == '@':
                return f"{element[1]}"
        return ""

    def loop(self, element, output_str=""):
        """Process loop body statements for JavaScript."""
        if isinstance(element[0], tuple):
            output_str += self.loop(element[0], output_str)
            output_str += self.loop(element[1], output_str)
        else:
            op = element[0]
            if op == 'ELSEIF':
                output_str += f"else if ({self.releval(element[1])}) {{ \n"
                output_str += f"\t{self.eval(element[2])} \n"
                output_str += f"}} \n"
            elif op == 'FUNC':
                output_str = f"ampfunctions['{element[1]}'](ampfunctions,{self.convert_value_to_string(element[2])});\n"
        return output_str

    def eval(self, element):
        """Evaluate an AST element to JavaScript code."""
        op = element[0]

        if op == 'VAR':
            if isinstance(element[1], tuple):
                flattened = self.flatten_list(element[1])
                for var in flattened:
                    if var != '@':
                        self.output += f"var {var};\n"
            else:
                self.output += f"var {element[2]};\n"
        elif op == 'SET':
            self.output += f"{element[1]} = {self.convert_value_to_string(element[2])};\n"
        elif op == 'IF':
            self.output += f"if ({self.releval(element[1])}) {{ \n"
            self.output += f"{self.loop(element[2])} \n"
            self.output += f"}} \n"
        elif op == 'IFELSE':
            self.output += f"if ({self.releval(element[1])}) {{ \n"
            self.output += f"{self.loop(element[2])} \n"
            self.output += f"}} \n"
            # Check if element[3] is an ELSEIFCHAIN or just statements
            if isinstance(element[3], tuple) and element[3][0] == 'ELSEIFCHAIN':
                self.output += f"{self.loop(element[3][1])}"  # Process elseif chain
                self.output += f"else {{ \n"
                self.output += f"{self.loop(element[3][2])} \n"  # Final else block
                self.output += f"}}\n"
            else:
                self.output += f"else {{ \n"
                self.output += f"{self.loop(element[3])} \n"
                self.output += f"}}\n"
        elif op == 'ELSEIF':
            # Handle chained ELSEIFs
            if len(element) == 3:
                # Single ELSEIF: ('ELSEIF', condition, statements)
                self.output += f"else if ({self.releval(element[1])}) {{ \n"
                self.output += f"{self.loop(element[2])} \n"
                self.output += f"}} \n"
            else:
                # Chained: ('ELSEIF', previous_chain, condition, statements)
                self.output += f"{self.loop(element[1])}"  # Process previous chain
                self.output += f"else if ({self.releval(element[2])}) {{ \n"
                self.output += f"{self.loop(element[3])} \n"
                self.output += f"}} \n"
        elif op == 'FOR':
            loopvar = element[1]
            initval = element[2]
            finval = element[4]
            stepval = element[5]
            direction = element[3]

            self.output += f"{loopvar} = {self.convert_value_to_string(initval)}\n"
            self.output += f"while ({loopvar} < {self.convert_value_to_string(finval)}) {{ \n"
            self.output += f"\t{self.loop(stepval)}"

            if direction == 'TO':
                self.output += f"\t{loopvar} += 1; \n"
            elif direction == 'DOWNTO':
                self.output += f"\t{loopvar} -= 1; \n"
            self.output += f"}} \n"
        elif op == '@':
            self.output += f"{element[1]} = '';\n"
        elif op == 'FUNC':
            func_call = f"ampfunctions['{element[1]}'](ampfunctions,{self.convert_value_to_string(element[2])});\n"
            self.output += func_call
