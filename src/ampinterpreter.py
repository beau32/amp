# -----------------------------------------------------------------------------
# amp-yacc.py

# Copyright (C) 2023
# B. Wang
# All rights reserved.
# Licensed under the BSD open source license agreement

# This compiler runs ampscript code
# -----------------------------------------------------------------------------

import sys,logging
from . import ampfunctions, ampyacc



class AmpInterpreter:

    # Initialize the interpreter. prog is a dictionary
    # containing (line,statement) mappings
    def __init__(self, prog):
        self.prog = prog
        self.functions = ampfunctions

        self.vars = {}            # All variables
        self.lists = {}            # List variables
        self.tables = {}            # Tables
        self.loops = []            # Currently active loops
        self.loopend = {}
        self.error = 0   
        self.pc = 0 

    # Evaluate an expression
    def eval(self, expr):
        if (expr == None):
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
            if hasattr(self.functions,var) :
                # A function
                func = getattr(self.functions,var)
                return func(self.functions, self.eval(expr[2]))
            else:
                print("UNDEFINED FUNCTION %s AT LINE %s" %
                    (var, self.stat[self.pc]))
                raise RuntimeError
        elif etype == 'INT':
            return int(expr[1])
        elif etype == 'STR':
            return str(expr[1])
        elif etype == '@':
            if expr[1] in self.vars:
                if isinstance(self.vars[expr[1]],int):
                    return int(self.vars[expr[1]])
                elif isinstance(self.vars[expr[1]], str):
                    return str(self.vars[expr[1]])
                elif isinstance(self.vars[expr[1]], float):
                    return float(self.vars[expr[1]])
            else:
                print("UNDEFINED VARIABLE @%s AT LINE %s" %
                        (expr[1], self.pc))
                raise RuntimeError

    # Evaluate a relational expression
    def releval(self, expr):
        etype = expr[1]
        lhs = self.eval(expr[2])
        rhs = self.eval(expr[3])
        return eval(f"{self.eval(expr[2])} {etype} {self.eval(expr[3])}")

    # Assignment
    def assign(self, target, value):   
        
        if value == None:
            self.vars[target] = None
        else:
            if target in self.vars:
                self.vars[target] = self.eval(value)
            else:
                print("UNDEFINED VARIABLE @%s AT LINE %s" %
                        (target, self.pc))
                raise RuntimeError
    def flatten_list(self, nested_list, result = []):
        for item in nested_list:
            if isinstance(item, tuple):
                self.flatten_list(item,result)
            else:
                result.append(item)
        return result
                    
    def interpret(self):

        self.stat = list(self.prog)  # Ordered list of all line numbers
        self.stat.sort()

        if self.error:
            raise RuntimeError

        line = self.stat[self.pc]
        instr = self.prog[line]

        op = instr[0]
        
        self.pc += 1

        if op == 'VAR':
            if isinstance(instr[1],tuple):
                flist = self.flatten_list(instr[1])
                for x in flist:
                    if x != '@':
                        self.assign(x, None)
            else:
                self.assign(instr[1], None)
        elif op == 'SET':
            target = instr[1]
            value = instr[2]
            
            if target in self.vars:
                self.assign(target, value)
            else:
                print("UNDEFINED VARIABLE @%s AT LINE %s" %
                      (instr[1], self.pc))
                raise RuntimeError
        elif op == '@':
            if (instr[1] in self.vars):
                print(self.vars[instr[1]])
            else:
                print("UNRECOGNISED VARIABLE @%s AT LINE %s" % (instr[1], self.pc))
                raise RuntimeError
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
                print("UNRECOGNISED NEXT VARIABLE @%s AT LINE %s" %
                      (finval, self.pc))
                raise RuntimeError 
            
            self.assign(loopvar, initval)
            if not stepval:
                stepval = ('INT', 1)

            if direction == 'TO':
                while (self.vars[loopvar]< self.eval(finval)):
                    self.eval(stepval)
                    self.vars[loopvar] +=1
            elif direction=='DOWNTO':
                while (self.vars[loopvar]> self.eval(finval)):
                    self.eval(stepval)
                    self.vars[loopvar] -=1
            del self.vars[loopvar]
        else:
            re = self.eval(instr)
            if (re):
                print(re)
        
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
                s = f"\tgetattr(ampfunctions,'{element[1]}')(ampfunctions,{self.var_str(element[2])})\n"
        return s
        
    # Utility functions for program listing
    def expr_str(self, expr):
        etype = expr[0]
        
        if etype == 'GROUP':
            return "(%s)" % self.expr_str(expr[1])
        elif etype == 'UNARY':
            if expr[1] == '-':
                return "-" + str(expr[2])
        elif etype == 'RELOP':
            return "%s %s %s" % (self.expr_str(expr[2]), expr[1], self.expr_str(expr[3]))
        elif etype == 'BINOP':
            return "%s %s %s" % (self.expr_str(expr[2]), expr[1], self.expr_str(expr[3]))
        elif etype == 'VAR':
            return self.var_str(expr[1])

    def relexpr_str(self, expr):
        return "%s %s %s" % (self.expr_str(expr[2]), expr[1], self.expr_str(expr[3]))

    def var_str(self, tup):

        if tup[0]=='INT':
            return f"{tup[1]}"
        elif tup[0] == 'STR':
            return f"'{tup[1]}'"
        elif tup[0] == '@':
            return f"{self.vars[tup[1]]}"

    # Erase the current program
    def new(self):
        self.prog = {}

    # Insert statements
    def add_statements(self, prog):
        self.prog[len(self.prog)] = prog