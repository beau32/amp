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
        if etype == '<':
            if lhs < rhs:
                return 1
            else:
                return 0

        elif etype == '<=':
            if lhs <= rhs:
                return 1
            else:
                return 0

        elif etype == '>':
            if lhs > rhs:
                return 1
            else:
                return 0

        elif etype == '>=':
            if lhs >= rhs:
                return 1
            else:
                return 0

        elif etype == '=':
            if lhs == rhs:
                return 1
            else:
                return 0

        elif etype == '<>':
            if lhs != rhs:
                return 1
            else:
                return 0

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
            for x in instr[1]:
                self.assign(x, None)
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
            if (self.releval(relop)):
                self.eval(newline)
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

    def var_str(self, var):
        varname, dim1, dim2 = var
        if not dim1 and not dim2:
            return varname
        if dim1 and not dim2:
            return "%s(%s)" % (varname, self.expr_str(dim1))
        return "%s(%s,%s)" % (varname, self.expr_str(dim1), self.expr_str(dim2))

    # Create a program listing
    def list(self):
        stat = list(self.prog)      # Ordered list of all line numbers
        stat.sort()
        for line in stat:
            instr = self.prog[line]
            op = instr[0]
            
            if op == 'VAR':
                print("%s VAR %s = %s" %
                      (line, self.var_str(instr[1]), self.expr_str(instr[2])))
            elif op == 'IF':
                print("%s IF %s THEN %d ENDIF"  %
                      (line, self.relexpr_str(instr[1]), instr[2]))
            elif op == 'FOR':
                _out = "%s FOR %s = %s TO %s" % (
                    line, instr[1], self.expr_str(instr[2]), self.expr_str(instr[3]))
                if instr[4]:
                    _out += " NEXT %s" % (self.expr_str(instr[4]))
                print(_out)
            elif op == 'NEXT':
                print("%s NEXT %s" % (line, instr[1]))
            

    # Erase the current program
    def new(self):
        self.prog = {}

    # Insert statements
    def add_statements(self, prog):
        self.prog[len(self.prog)] = prog