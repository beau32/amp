#!/usr/bin/env python3
"""Debug wrapper transpilation with markers in place."""

import sys
import os
import re

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Read file
with open('codesample_js_advanced.ampscript', 'r') as f:
    content = f.read()

# Replace AmpScript blocks with markers (as the compile function does)
ampscript_blocks = []
wrapper = content
for i, match in enumerate(re.finditer(r'%%\[[\s\S]*?\]%%', content)):
    ampscript_blocks.append(match.group(0))
    wrapper = wrapper.replace(match.group(0), f'###AMPSCRIPT_BLOCK_{i}###', 1)

print("=== WRAPPER WITH MARKERS (lines 1-50) ===")
for i, line in enumerate(wrapper.split('\n')[:50], 1):
    print(f"{i:2d}: {line}")

# Now import and call transpile_js_to_py on the wrapper
from amp import transpile_js_to_py

print("\n=== TRANSPILING WRAPPER ===")
result = transpile_js_to_py(wrapper)

print("\n=== TRANSPILED (lines 1-30) ===")
for i, line in enumerate(result.split('\n')[:30], 1):
    print(f"{i:2d}: {line}")

print("\n=== LOOKING FOR FOR/WHILE/THRESHOLD ===")
for i, line in enumerate(result.split('\n')):
    if any(kw in line for kw in ['while', 'for', 'threshold', 'FOR_LOOP']):
        print(f"Line {i}: {line}")
