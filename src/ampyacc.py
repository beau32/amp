# =============================================================================
# ampyacc.py
#
# Copyright (C) 2023 B. Wang
# All rights reserved.
# Licensed under the BSD open source license agreement
#
# Parser for AmpScript language using PLY.
# =============================================================================
"""Parser for AmpScript language using PLY yacc."""

import ply.yacc as yacc
from . import amplex

tokens = amplex.tokens

# Operator precedence and associativity
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE'),  # All comparison operators at same level
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
    ('right', 'NOT'),
    ('nonassoc', 'ELSE'),  # Resolve dangling-else by preferring shift
)


def p_program(p):
    """program : OPEN statements CLOSE
                | SOPEN expression SCLOSE
                | statements"""
    if p[1] == "%%=" or p[1] == "%%[":
        p[0] = p[2]
    else:
        p[0] = p[1]


def p_program_error(p):
    """program : error"""
    p[0] = None
    p.parser.error = 1



def p_statements(p):
    """statements : statements statement
                  | statement"""
    if len(p) == 3:
        p[0] = (p[1], p[2])
    elif len(p) == 2:
        p[0] = p[1]


def p_statement_fordo(p):
    """statement : FOR '@' NAME '=' expression TO expression DO statements NEXT '@' NAME
                 | FOR '@' NAME '=' expression DOWNTO expression DO statements NEXT '@' NAME"""
    p[0] = ('FOR', p[3], p[5], p[6], p[7], p[9], p[12])


def p_statement_if(p):
    """statement : IF expression THEN statements endif_else"""
    if p[5] is None:
        p[0] = ('IF', p[2], p[4])
    elif isinstance(p[5], tuple) and p[5][0] == 'ELSEIFCHAIN':
        p[0] = ('IFELSE', p[2], p[4], p[5])
    else:
        p[0] = ('IFELSE', p[2], p[4], p[5])


def p_endif_else(p):
    """endif_else : elseiflist ELSE statements ENDIF
                  | ELSE statements ENDIF  
                  | ENDIF"""
    if len(p) == 5:
        # Has elseiflist + else
        p[0] = ('ELSEIFCHAIN', p[1], p[3])
    elif len(p) == 4:
        # Just else
        p[0] = p[2]
    else:
        # Just endif
        p[0] = None


def p_elseiflist(p):
    """elseiflist : elseiflist ELSEIF expression THEN statements
                  | ELSEIF expression THEN statements"""
    if len(p) == 6:
        p[0] = ('ELSEIF', p[1], p[3], p[5])
    else:
        p[0] = ('ELSEIF', p[2], p[4])


def p_condition_condibracket(p):
    """expression : "(" expression ")" """
    p[0] = ('GROUP', p[2])


def p_condition_logic(p):
    """expression : expression EQ expression
                  | expression GE expression
                  | expression LE expression
                  | expression LT expression
                  | expression GT expression
                  | expression NE expression"""
    p[0] = ('RELOP', p[2], p[1], p[3])


def p_statement_declare(p):
    """statement : VAR list"""
    p[0] = ('VAR', p[2])


def p_statement_assign(p):
    """statement : SET "@" NAME "=" expression"""
    p[0] = ('SET', p[3], p[5])


def p_statement_expr(p):
    """statement : expression"""
    p[0] = p[1]


def p_expression_calcop(p):
    """expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression
                  | expression AND expression
                  | expression OR expression"""
    p[0] = ('BINOP', p[2], p[1], p[3])


def p_expression_uminus(p):
    """expression : '-' expression %prec UMINUS"""
    p[0] = -p[2]


def p_expression_not(p):
    """expression : NOT expression"""
    pass


def p_expression_func(p):
    """expression : NAME '(' expression ',' expression ')'
                  | NAME '(' expression ')'
                  | NAME '(' ')'"""
    if len(p) == 4:
        p[0] = ('FUNC', p[1])
    elif len(p) == 5:
        p[0] = ('FUNC', p[1], p[3])
    else:
        p[0] = ('FUNC', p[1], p[3], p[5])


def p_expression_number(p):
    """expression : NUMBER
                  | STRING"""
    p[0] = (type(p[1]).__name__.upper(), p[1])


def p_expression_name(p):
    """expression : '@' NAME"""
    p[0] = ('@', p[2])


def p_expression_name_error(p):
    """expression : '@' NAME error"""
    pass


def p_expression_commaname(p):
    """list : list ',' '@' NAME
           | '@' NAME"""
    if len(p) > 3:
        p[0] = (p[1], '@', p[4])
    else:
        p[0] = (p[1], p[2])


def p_expression_commaname_error(p):
    """list : list ',' '@' NAME  error
            | '@' NAME error"""
    pass


def p_error(p):
    """Handle syntax errors."""
    if p:
        print("Syntax error at '%s' on line '%s'" % (p.value, p.lexer.lineno))
    else:
        print("Syntax error at EOF")


# Build the parser
ampparser = yacc.yacc()


def parse(data, debug=0):
    """
    Parse AmpScript code.

    Args:
        data: AmpScript source code string
        debug: Debug logging object (optional)

    Returns:
        Parsed AST or None if parsing failed
    """
    ampparser.error = 0
    parsed = ampparser.parse(data, debug=debug)

    if ampparser.error:
        return None
    return parsed
