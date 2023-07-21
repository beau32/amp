# -----------------------------------------------------------------------------
# amp-yacc.py

# Copyright (C) 2023
# B. Wang
# All rights reserved.
# Licensed under the BSD open source license agreement

# This compiler runs ampscript code
# -----------------------------------------------------------------------------

from ply import *

keywords = ('SET','IF', 'FOR','THEN','AND','OR','ELSE','ENDIF','NEXT','DO','TO','DOWNTO','ELSEIF','NOT','VAR','OPEN','CLOSE','SOPEN', 'SCLOSE')

tokens = keywords + (
    'NAME', 'NUMBER', 'STRING','EQ','GE','LE','NE','LT','GT'
)

literals = ['=', '+', '-', '*', '/', '(', ')','@','\"','\"',',','%','[',']']

# Tokens

def t_NAME(t) :
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in keywords:
        t.type = t.value
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"\w+\"'
    t.value = str(t.value.replace('"',''))
    return t

t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_COMMENT(t):
    r'\/\*.*\*\/'
    pass

# Parsing rules
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_NE = r'!='
t_EQ = r'=='
t_OPEN= r'\%\%\['
t_CLOSE = r'\]\%\%'
t_SOPEN= r'\%\%\='
t_SCLOSE = r'\=\%\%'

# Build the lexer
lex.lex()
