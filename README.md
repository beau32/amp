# amp
PLY(lex/yacc) based AMPscript compiler to aide Salesforce Marketing Cloud local development and exprimentation. This tool runs in interpreter and compiler mode. In compiler mode, it takes an ampscript file as input and outputs JavaScript or Python.

## Features
- AMPscript interpreter and compiler
- JavaScript + AMPscript mixed blocks (%%[ ... ]%% inside `<script runat='server'>`)
- JavaScript to Python transpilation with:
	- implicit string coercion for `+`
	- `.length` to `len()` conversion
	- object property access converted to dict access
	- `console.*` and `Write()` mapped to ampfunctions
- AMPscript function library in `src/ampfunctions.py` with dynamic delegation

## Install
```
git clone https://github.com/beau32/amp.git
cd amp
pip3 install -r requirement.txt
```

## Run
### Interpreter
```
python3 amp.py
```

### Compile to JavaScript or Python
```
python3 amp.py -l js -i codesample.ampscript > output.js

python3 amp.py -l py -i codesample.ampscript > output.py
```

### Execute compiled Python directly
```
python3 amp.py -l py -i codesample.ampscript | python3 -
```

## Samples
- `codesample.ampscript`: AMPscript only
- `codesample_js.ampscript`: JavaScript + AMPscript
- `codesample_js_advanced.ampscript`: advanced mixed example
- `test_nested_if.ampscript`: nested IF test
- `test_nested_set.ampscript`: expression assignment test

## Notes
- JavaScript object literals are converted to Python `dict()`.
- AMPscript variables use the `_amp` suffix in generated Python.
- When transpiling JS to Python, `console.log/warn/error/info` and `Write()` route to `ampfunctions.Write()`.
