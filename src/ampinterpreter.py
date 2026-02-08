# =============================================================================
# ampinterpreter.py
#
# Copyright (C) 2023 B. Wang
# All rights reserved.
# Licensed under the BSD open source license agreement
#
# Interpreter for executing AmpScript AST.
# =============================================================================
"""Interpreter for executing AmpScript AST."""

import logging
from . import ampfunctions, ampyacc


logger = logging.getLogger(__name__)


class AmpInterpreter:
    """Interpreter for executing AmpScript AST."""

    def __init__(self, prog):
        """
        Initialize the interpreter with a program dictionary.

        Args:
            prog: Dictionary containing (line, statement) mappings
        """
        self.prog = prog
        self.functions = ampfunctions.func()

        self.vars = {}          # All variables
        self.lists = {}         # List variables
        self.tables = {}        # Table definitions
        self.loops = []         # Currently active loop stack
        self.loopend = {}       # Loop end conditions
        self.error = 0          # Error flag
        self.pc = 0             # Program counter

    def eval(self, expr):
        """
        Evaluate an expression and return its value.

        Args:
            expr: Expression tuple from AST

        Returns:
            Expression result or None
        """
        if expr is None:
            return None

        etype = expr[0]

        if etype == 'GROUP':
            return self.eval(expr[1])
        elif etype == 'UNARY':
            if expr[1] == '-':
                return -self.eval(expr[2])
        elif etype == 'RELOP':
            return str(eval(f'{self.eval(expr[2])} {expr[1]} {self.eval(expr[3])}'))
        elif etype == 'BINOP':
            if expr[1] == '+':
                return self.eval(expr[2]) + self.eval(expr[3])
            elif expr[1] == '-':
                return self.eval(expr[2]) - self.eval(expr[3])
            elif expr[1] == '*':
                return self.eval(expr[2]) * self.eval(expr[3])
            elif expr[1] == '/':
                return float(self.eval(expr[2])) / self.eval(expr[3])
        elif etype == 'FUNC':
            var = expr[1]
            if hasattr(self.functions, var):
                func = getattr(self.functions, var)
                return func(self.eval(expr[2]))
            else:
                logger.error("UNDEFINED FUNCTION %s AT LINE %s", var, self.pc)
                raise RuntimeError(f"Undefined function: {var}")
        elif etype == 'INT':
            return int(expr[1])
        elif etype == 'STR':
            return str(expr[1])
        elif etype == '@':
            if expr[1] in self.vars:
                value = self.vars[expr[1]]
                if isinstance(value, int):
                    return int(value)
                elif isinstance(value, str):
                    return str(value)
                elif isinstance(value, float):
                    return float(value)
            else:
                logger.error("UNDEFINED VARIABLE @%s AT LINE %s", expr[1], self.pc)
                raise RuntimeError(f"Undefined variable: @{expr[1]}")

    def releval(self, expr):
        """
        Evaluate a relational expression.

        Args:
            expr: Relational expression tuple

        Returns:
            Boolean result
        """
        lhs = self.eval(expr[2])
        rhs = self.eval(expr[3])
        return eval(f"{lhs} {expr[1]} {rhs}")

    def assign(self, target, value):
        """
        Assign a value to a variable.

        Args:
            target: Variable name
            value: Value to assign
        """
        if value is None:
            self.vars[target] = None
        else:
            if target in self.vars:
                self.vars[target] = self.eval(value)
            else:
                logger.error("UNDEFINED VARIABLE @%s AT LINE %s", target, self.pc)
                raise RuntimeError(f"Undefined variable: @{target}")

    def flatten_list(self, nested_list, result=None):
        """
        Flatten a nested list structure.

        Args:
            nested_list: Nested list from AST
            result: Accumulator list

        Returns:
            Flattened list
        """
        if result is None:
            result = []
        for item in nested_list:
            if isinstance(item, tuple):
                self.flatten_list(item, result)
            else:
                result.append(item)
        return result

    def interpret(self):
        """Execute the program statements in order."""
        self.stat = list(self.prog)  # Ordered list of all line numbers
        self.stat.sort()

        if self.error:
            raise RuntimeError("Previous error detected")

        line = self.stat[self.pc]
        instr = self.prog[line]

        op = instr[0]
        self.pc += 1

        if op == 'VAR':
            if isinstance(instr[1], tuple):
                flist = self.flatten_list(instr[1])
                for var in flist:
                    if var != '@':
                        self.assign(var, None)
            else:
                self.assign(instr[1], None)
        elif op == 'SET':
            target = instr[1]
            value = instr[2]

            if target in self.vars:
                self.assign(target, value)
            else:
                logger.error("UNDEFINED VARIABLE @%s AT LINE %s", instr[1], self.pc)
                raise RuntimeError(f"Undefined variable: @{instr[1]}")
        elif op == '@':
            if instr[1] in self.vars:
                print(self.vars[instr[1]])
            else:
                logger.error("UNRECOGNISED VARIABLE @%s AT LINE %s", instr[1], self.pc)
                raise RuntimeError(f"Unrecognised variable: @{instr[1]}")
        elif op == 'IF':
            relop = instr[1]
            newline = instr[2]
            output = ''
            output += f"if {self.releval(relop)}: \n"
            output += self.loop(newline)
            exec(output)
        elif op == 'IFELSEIF':
            output = ''
            output += f"if {self.releval(instr[1])}: \n"
            output += f"{self.loop(instr[2])} \n"
            output += f"{self.loop(instr[3])} \n"
            output += f"else: \n"
            output += f"{self.loop(instr[4])} \n"
            exec(output)
        elif op == 'IFELSE':
            output = ''
            output += f"if {self.releval(instr[1])}: \n"
            output += f"{self.loop(instr[2])}"
            output += f"else: \n"
            output += f"{self.loop(instr[3])}"
            exec(output)
        elif op == 'FOR':
            loopvar = instr[1]
            initval = instr[2]
            finval = instr[4]
            stepval = instr[5]
            nextval = instr[6]
            direction = instr[3]

            if loopvar not in self.vars:
                self.assign(loopvar, None)

            if loopvar != nextval:
                logger.error("UNRECOGNISED NEXT VARIABLE @%s AT LINE %s", finval, self.pc)
                raise RuntimeError(f"Unrecognised next variable: @{finval}")

            self.assign(loopvar, initval)
            if not stepval:
                stepval = ('INT', 1)

            if direction == 'TO':
                while self.vars[loopvar] < self.eval(finval):
                    self.eval(stepval)
                    self.vars[loopvar] += 1
            elif direction == 'DOWNTO':
                while self.vars[loopvar] > self.eval(finval):
                    self.eval(stepval)
                    self.vars[loopvar] -= 1
            del self.vars[loopvar]
        else:
            result = self.eval(instr)
            if result:
                print(result)

    def loop(self, element, output_str=""):
        """
        Process loop body statements.

        Args:
            element: Loop body element from AST
            output_str: Accumulated output string

        Returns:
            Generated Python code string
        """
        if isinstance(element[0], tuple):
            output_str += self.loop(element[0], output_str)
            output_str += self.loop(element[1], output_str)
        else:
            op = element[0]

            if op == 'ELSEIF':
                output_str += f"elif {self.releval(element[1])}: \n"
                output_str += f"\t{self.eval(element[2])} \n"
            elif op == 'FUNC':
                output_str = f"\tgetattr(ampfunctions,'{element[1]}')({self.var_str(element[2])})\n"
        return output_str

    def expr_str(self, expr):
        """
        Convert an expression tuple to a string representation.

        Args:
            expr: Expression tuple from AST

        Returns:
            String representation
        """
        etype = expr[0]

        if etype == 'GROUP':
            return f"({self.expr_str(expr[1])})"
        elif etype == 'UNARY':
            if expr[1] == '-':
                return "-" + str(expr[2])
        elif etype == 'RELOP':
            return f"{self.expr_str(expr[2])} {expr[1]} {self.expr_str(expr[3])}"
        elif etype == 'BINOP':
            return f"{self.expr_str(expr[2])} {expr[1]} {self.expr_str(expr[3])}"
        elif etype == 'VAR':
            return self.var_str(expr[1])

    def relexpr_str(self, expr):
        """Convert relational expression to string."""
        return f"{self.expr_str(expr[2])} {expr[1]} {self.expr_str(expr[3])}"

    def var_str(self, tup):
        """Convert a value tuple to string."""
        if tup[0] == 'INT':
            return f"{tup[1]}"
        elif tup[0] == 'STR':
            return f"'{tup[1]}'"
        elif tup[0] == '@':
            return f"{self.vars.get(tup[1], '')}"

    def new(self):
        """Clear the program."""
        self.prog = {}

    def add_statements(self, prog):
        """
        Add statements to the program.

        Args:
            prog: Statement tuple to add
        """
        self.prog[len(self.prog)] = prog