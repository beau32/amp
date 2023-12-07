# -----------------------------------------------------------------------------
# amp-yacc.py

# Copyright (C) 2023
# B. Wang
# All rights reserved.
# Licensed under the BSD open source license agreement

# This compiler runs ampscript code
# -----------------------------------------------------------------------------

import sys,logging
from src import ampinterpreter, ampyacc, ampcompiler
import argparse
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

logging.basicConfig(
    level=logging.INFO,
    filename="parse.log",
    filemode="w"
)
parser = argparse.ArgumentParser(description='Amp with command-line arguments')

    # Add the command-line arguments
parser.add_argument('-l', '--language', type=str, help='js or py')
parser.add_argument('-i', '--input', type=str, help='input file')
args = parser.parse_args()
arguments = []
arguments.append(args.language)
arguments.append(args.input)

if len(arguments) == 2:
    
    with open(args.input) as f:
        data = f.read()
        
    prog = ampyacc.parse(data)
    if not prog:
        raise SystemExit
    if args.language == 'py':
        b = ampcompiler.AmpCompilerToPy(prog)
    elif args.language == 'js':
        b = ampcompiler.AmpCompilerToJs(prog)
    
    try:
        b.compile()
        raise SystemExit
    except RuntimeError:
        pass
else:
    b = ampinterpreter.AmpInterpreter({})

    print('(o) Amp 0.0.5')
    while True:
        try:
            s = prompt('amp > ',history=FileHistory('.history.txt'),auto_suggest=AutoSuggestFromHistory())
        except EOFError:
            break
        if not s:
            continue
        s += "\n"
        
        prog = ampyacc.parse(s, debug=logging.getLogger())
        
        if not prog:
            continue
        
        try:
            b.add_statements(prog)
            b.interpret()
        except RuntimeError as e:
            pass