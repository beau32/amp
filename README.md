# amp
Open Source PLY(lex/yacc) based Ampscript compiler to aide SFMC (Salesforce Marketing Cloud) local development and exprimentation. This tool runs in interpreter and compiler mode. In compiler model, it takes an ampscript file as input, and output python code.


to install
```
git clone https://github.com/beau32/amp.git
cd amp
pip3 install -r requirement.txt
```

to launch the intrepeter
```
python3 amp.py
```

to launch the compiler and transcode to python
```
python3 amp.py codesample.ampscript > output.py
```
