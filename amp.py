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
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

logging.basicConfig(
    level=logging.INFO,
    filename="parse.log",
    filemode="w"
)

if len(sys.argv) == 2:
    with open(sys.argv[1]) as f:
        data = f.read()
    
    prog = ampyacc.parse(data)
    if not prog:
        raise SystemExit
    b = ampcompiler.AmpCompiler(prog)
    
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