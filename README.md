# amp
Open Source lex/yacc based ampscript compiler to aide SFMC local development and exprimentation. This tool runs in interpreter and compiler mode, in compiler model, it takes an ampscript file as input, and output python code.


to install
```
pip3 install amp
```

to launch the intrepeter
```
python3 amp.py
```

to launch the compiler and transcode to python
```
python3 amp.py codesample.ampscript > output.py
```