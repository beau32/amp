import sys
import ampyacc
from ampinterpreter import AmpInterpreter
from ampcompiler import AmpCompiler
import logging

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
    b = AmpCompiler(prog)
    
    try:
        b.compile()
        raise SystemExit
    except RuntimeError:
        pass
else:
    b = AmpInterpreter({})

    print('(o) Amp 0.0.5')
    while True:
        try:
            s = input('amp > ')
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