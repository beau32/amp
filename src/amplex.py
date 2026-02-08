# =============================================================================
# amplex.py
#
# Copyright (C) 2023 B. Wang
# All rights reserved.
# Licensed under the BSD open source license agreement
#
# Lexical analyzer for AmpScript language using PLY.
# =============================================================================
"""Tokenizer for AmpScript language using PLY lexer."""

import ply.lex as lex

# Reserved keywords in AmpScript
AMPSCRIPT_KEYWORDS = (
    'SET', 'IF', 'FOR', 'THEN', 'AND', 'OR', 'ELSE', 'ENDIF',
    'NEXT', 'DO', 'TO', 'DOWNTO', 'ELSEIF', 'NOT', 'VAR',
    'OPEN', 'CLOSE', 'SOPEN', 'SCLOSE'
)

# Keywords
KEYWORDS = AMPSCRIPT_KEYWORDS

# Token types
tokens = KEYWORDS + (
    'NAME', 'NUMBER', 'STRING', 'EQ', 'GE', 'LE', 'NE', 'LT', 'GT'
)

# Single-character tokens
literals = ['=', '+', '-', '*', '/', '(', ')', '@', '"', ',', '%', '[', ']']


def t_NAME(token):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Check if it's an AmpScript keyword
    if token.value in AMPSCRIPT_KEYWORDS:
        token.type = token.value
    return token


def t_NUMBER(token):
    r'\d+'
    token.value = int(token.value)
    return token


def t_STRING(token):
    r'"[^"]*"'
    # Remove quotes and store the content
    token.value = str(token.value[1:-1])
    return token


# Ignored characters (whitespace)
t_ignore = " \t"


def t_newline(token):
    r'\n+'
    token.lexer.lineno += token.value.count("\n")


def t_error(token):
    """Handle illegal characters."""
    print("Illegal character '%s'" % token.value[0])
    token.lexer.skip(1)


def t_COMMENT(token):
    r'\/\*.*?\*\/'
    pass


# Comparison and assignment operators
t_LE = r'<='
t_GE = r'>='
t_NE = r'!='
t_EQ = r'=='
t_LT = r'<'
t_GT = r'>'

# AmpScript tag delimiters
t_OPEN = r'\%\%\['
t_CLOSE = r'\]\%\%'
t_SOPEN = r'\%\%\='
t_SCLOSE = r'\=\%\%'

# Build the lexer
lexer = lex.lex()


