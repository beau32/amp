# -----------------------------------------------------------------------------
# amp-yacc.py

# Copyright (C) 2023
# B. Wang
# All rights reserved.
# Licensed under the BSD open source license agreement

# This compiler runs ampscript code
# -----------------------------------------------------------------------------

import sys, logging
from . import ampyacc

output = ''


class AmpCompilerToPy:
    def __init__(self,tree) -> None:
        self.tree = tree

    def compile(self):
        global output
        output += "from src import ampfunctions\n"

        self.walk_tree(self.tree)
        print(output)
    
    #walk through the nested list based using b-tree
    def walk_tree(self,tree):  
        if isinstance(tree,tuple):
            if isinstance(tree[0],tuple):
                self.walk_tree(tree[0]) #process the head
                self.walk_tree(tree[1]) #process the tail
            self.eval(tree)
                
    def str_val(self,tup):
        if tup[0]=='INT':
            return f"{tup[1]}"
        elif tup[0] == 'STR':
            return f"'{tup[1]}'"
        elif tup[0] == '@':
            return f"{tup[1]}"

    def eval(self, element):
        global output

        op = element[0]

        if op=='VAR':
            if isinstance(element[1],tuple):
                flattened = []
                flattened = self.flatten_list(element[1])
                for x in flattened:
                    if x != '@':
                        output += f"{x} = None\n"
            else:
                output += f"{element[2]} = None\n"
        elif op=='SET':
            output += f"{element[1]} = {self.str_val(element[2])}\n"
        elif op == 'IF':
            output += f"if {self.releval(element[1])}: \n"
            output += f"{self.loop(element[2])} \n"
        elif op == 'IFELSEIF':
            output += f"if {self.releval(element[1])}: \n"
            output += f"{self.loop(element[2])} \n"

            output += f"{self.loop(element[3])} \n"
            output += f"else: \n"
            output += f"{self.loop(element[4])} \n"
        elif op == 'IFELSE':
            output += f"if {self.releval(element[1])}: \n"
            output += f"{self.loop(element[2])}"
            output += f"else: \n"
            output += f"{self.loop(element[3])}"
        elif op == 'FOR':
            loopvar = element[1]
            initval = element[2]
            finval = element[4]
            stepval = element[5]
            nextval = element[6]
            direction = element[3]
            
            output += f"{loopvar} = {self.str_val(initval)}\n"
            output += f"while {loopvar} < {self.str_val(finval)}: \n"
            output += f"{self.loop(stepval)}"
            
            if direction == 'TO':
                output += f"\t{loopvar}+=1 \n"
            elif direction=='DOWNTO':
                output += f"\t{loopvar}-=1 \n"
        elif op == '@':
            output += f"{element[1]} = None\n"
        elif op=='FUNC':
            s = f"getattr(ampfunctions,'{element[1]}')(ampfunctions,{self.str_val(element[2])})\n"
            output += s
            return s

    def flatten_list(self, nested_list, flattened = []):
        for item in nested_list:
            if isinstance(item, tuple):
                self.flatten_list(item,flattened)
            else:
                flattened.append(item)
        return flattened

    def releval(self, element):
        if isinstance(element[0], tuple):
                self.loop(element[0])
                self.loop(element[1])
        else:
            op = element[0]
            if op == 'GROUP':
                return f"{self.releval(element[1])}"
            elif op == 'RELOP' or op == 'BINOP':
                return f"{self.releval(element[2])} {element[1].lower()} {self.releval(element[3])}"
            elif op == '@':
                return f"{element[1]}"
    
    def loop(self, element, s=''):
        if isinstance(element[0], tuple):
                s += self.loop(element[0],s)
                s += self.loop(element[1],s)
        else:
            op = element[0]
            
            if op == 'ELSEIF':
                s += f"elif {self.releval(element[1])}: \n"
                s += f"\t{self.eval(element[2])} \n"
            elif op == 'FUNC' :
                s = f"\tgetattr(ampfunctions,'{element[1]}')(ampfunctions,{self.str_val(element[2])})\n"
        return s
    

class AmpCompilerToJs:
    def __init__(self,tree) -> None:
        self.tree = tree

    def compile(self):
        global output

        self.walk_tree(self.tree)
        print(output)
    
    #walk through the nested list based using b-tree
    def walk_tree(self,tree):  
        if isinstance(tree,tuple):
            if isinstance(tree[0],tuple):
                self.walk_tree(tree[0]) #process the head
                self.walk_tree(tree[1]) #process the tail
            self.eval(tree)
                
    def str_val(self,tup):
        if tup[0]=='INT':
            return f"{tup[1]}"
        elif tup[0] == 'STR':
            return f"'{tup[1]}'"
        elif tup[0] == '@':
            return f"{tup[1]}"

    def eval(self, element):
        global output

        op = element[0]

        if op=='VAR':
            if isinstance(element[1],tuple):
                flattened = []
                flattened = self.flatten_list(element[1])
                for x in flattened:
                    if x != '@':
                        output += f"var {x};\n"
            else:
                output += f"var {element[2]};\n"
        elif op=='SET':
            output += f"{element[1]} = {self.str_val(element[2])};\n"
        elif op == 'IF':
            output += f"if ({self.releval(element[1])}) {{ \n"
            output += f"{self.loop(element[2])} \n"
            output += f"}} \n"
        elif op == 'IFELSEIF':
            output += f"if ({self.releval(element[1])}) {{ \n"
            output += f"{self.loop(element[2])} \n"
            output += f" }} \n"
            output += f"{self.loop(element[3])} \n"

            output += f"else {{ \n"
            output += f"{self.loop(element[4])} \n"
            output += f" }} \n"
        elif op == 'IFELSE':
            output += f"if {self.releval(element[1])} {{ \n"
            output += f"{self.loop(element[2])} \n"
            output += f" }} \n"
            output += f"else {{ \n"
            output += f"{self.loop(element[3])} \n"
            output += f"}} }}"
        elif op == 'FOR':
            loopvar = element[1]
            initval = element[2]
            finval = element[4]
            stepval = element[5]
            nextval = element[6]
            direction = element[3]
            
            output += f"{loopvar} = {self.str_val(initval)}\n"
            output += f"while ({loopvar} < {self.str_val(finval)}) {{ \n"
            output += f"\t{self.loop(stepval)}"
            
            if direction == 'TO':
                output += f"\t{loopvar}+=1; \n"
            elif direction=='DOWNTO':
                output += f"\t{loopvar}-=1; \n"
            output += f"}} \n"
        elif op == '@':
            output += f"{element[1]} = ''\n"
        elif op=='FUNC':
            s = f"ampfunctions[{element[1]}]({self.str_val(element[2])});\n"
            output += s
            return s

    def flatten_list(self, nested_list, flattened = []):
        for item in nested_list:
            if isinstance(item, tuple):
                self.flatten_list(item,flattened)
            else:
                flattened.append(item)
        return flattened

    def releval(self, element):
        if isinstance(element[0], tuple):
                self.loop(element[0])
                self.loop(element[1])
        else:
            op = element[0]
            if op == 'GROUP':
                return f"{self.releval(element[1])}"
            elif op == 'RELOP' or op == 'BINOP':
                sign = ''
                if element[1].lower()=='and':
                    sign = '&&'
                elif element[1].lower() == 'or':
                    sign = '||'
                else:
                    sign = element[1].lower()

                return f"{self.releval(element[2])} {sign} {self.releval(element[3])}"
            elif op == '@':
                return f"{element[1]}"
    
    def loop(self, element, s=''):
        if isinstance(element[0], tuple):
                s += self.loop(element[0],s)
                s += self.loop(element[1],s)
        else:
            op = element[0]
            
            if op == 'ELSEIF':
                s += f"elseif ({self.releval(element[1])}) {{ \n"
                s += f"\t{self.eval(element[2])} \n"
                s += f"}} \n"
            elif op == 'FUNC' :
                s = f"ampfunctions[{element[1]}]({self.str_val(element[2])});\n"
        return s