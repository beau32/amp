#!/usr/bin/env python3
"""Test with actual codesample_js_advanced.ampscript to find where corruption happens."""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the transpile function
from amp import transpile_js_to_py

# Read the advanced sample
with open('codesample_js_advanced.ampscript', 'r') as f:
    content = f.read()

# Find the JavaScript wrapper (before first %%[ )
ampscript_marker = '%%['
wrapper_end = content.find(ampscript_marker)
if wrapper_end > 0:
    js_wrapper = content[:wrapper_end]
else:
    js_wrapper = content

print("=== JAVASCRIPT WRAPPER (first 30 lines) ===")
for i, line in enumerate(js_wrapper.split('\n')[:30]):
    print(f"{i:2d}: {line}")

print("\n=== RUNNING TRANSPILE ===")
result = transpile_js_to_py(js_wrapper)

print("\n=== TRANSPILED OUTPUT (first 30 lines) ===")
for i, line in enumerate(result.split('\n')[:30]):
    print(f"{i:2d}: {line}")

# Search for the for loop
print("\n=== LOOKING FOR FOR LOOP ===")
for i, line in enumerate(result.split('\n')):
    if 'while' in line or 'for' in line or 'FOR_LOOP' in line:
        print(f"Line {i}: {line}")
