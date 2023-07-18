# -----------------------------------------------------------------------------
# amp-yacc.py

# Copyright (C) 2023
# B. Wang
# All rights reserved.
# Licensed under the BSD open source license agreement

# This compiler runs ampscript code
# -----------------------------------------------------------------------------

from ply import *
from . import amplex

tokens = amplex.tokens

precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('left', 'AND', 'OR'),
    ('right', 'UMINUS'),
)

def p_program(p):
    '''program : OPEN statements CLOSE
                | SOPEN expression SCLOSE
                | statements'''
    
    if p[1]== "%%=" or p[1] == "%%[":
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_statements(p):
    '''statements : statements statement
                | statement'''
    
    if len(p)==3:
        p[0] = (p[1],p[2])
    elif len(p) == 2:
        p[0] = p[1]

def p_program_error(p):
    '''program : error'''
    p[0] = None
    p.parser.error = 1

def p_statement_fordo(p):
    '''statement : FOR '@' NAME '=' expression TO expression DO statements NEXT '@' NAME
        statement : FOR '@' NAME '=' expression DOWNTO expression DO statements NEXT '@' NAME
    '''
    p[0] = ('FOR', p[3], p[5], p[6], p[7], p[9],p[12])



def p_statement_ifelseif(p):
    '''statement : IF expression THEN statements elseifchain ELSE statements ENDIF
                 | IF expression THEN statements ELSE statements ENDIF
                 | IF expression THEN statements ENDIF
    '''
    if len(p)==9:
        p[0] = ('IFELSEIF', p[2], p[4], p[5],p[7])
    elif len(p) == 8: 
        p[0] = ('IFELSE', p[2], p[4], p[6])
    elif len(p) == 6: 
        p[0] = ('IF', p[2], p[4])
    
def p_ifelseif_elseif(p):
    '''elseifchain : elseifchain ELSEIF expression THEN statements 
                    | ELSEIF expression THEN statements'''
    p[0] = ('ELSEIF',p[3], p[6])
        
    
def p_condition_condibracket(p):
    ''' expression : "(" expression ")"
    '''
    
    p[0] = ('GROUP',p[2])

def p_condition_logic(p):
    '''expression : expression AND expression
                | expression OR expression
                | expression EQ expression
                | expression GE expression
                | expression LE expression
                | expression LT expression
                | expression GT expression
                | expression NE expression
                '''
    p[0] = ('RELOP', p[2], p[1], p[3])
    
def p_statement_declare(p):
    '''statement : VAR list
    '''
    p[0] = ('VAR', p[2])
    
def p_statement_assign(p):
    '''statement : SET "@" NAME "=" expression
    '''
    p[0] = ('SET', p[3], p[5])
    
def p_statement_expr(p):
    '''statement : expression
    '''
    p[0] = p[1]

def p_expression_calcop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression
                  '''
    p[0] = ('BINOP', p[2], p[1], p[3])

    
def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]

def p_expression_not(p):
    '''expression : NOT expression'''

def p_expression_func(p):
    """expression : NAME '(' expression ',' expression ')'
                  | NAME '(' expression ')'
                  | NAME '(' ')'
    """
    if len(p) == 4:
        p[0] = ('FUNC', p[1])
    elif len(p) ==5:
        p[0] = ('FUNC', p[1],p[3])
    else:
        p[0] = ('FUNC', p[1], p[3], p[5])

def p_expression_number(p):
    """expression : NUMBER
                  | STRING
    """
    p[0] = (type(p[1]).__name__.upper(),p[1])
    
def p_expression_name(p):
    """expression : '@' NAME"""
    p[0] = ('@', p[2])

def p_expression_commaname(p):
    """list : list ',' '@' NAME
            | '@' NAME
    """

    if len(p) > 3:
        p[0] = (p[1], '@', p[4])
    else:
        p[0] = (p[1],p[2])

def p_error(p):
    if p:
        print("Syntax error at '%s' on line '%s'" % (p.value, p.lexer.lineno))
    else:
        print("Syntax error at EOF")

import ply.yacc as yacc
ampparser = yacc.yacc()

def parse(data, debug=0):
    ampparser.error = 0
    p = ampparser.parse(data, debug=debug)
    
    if ampparser.error:
        return None
    return p