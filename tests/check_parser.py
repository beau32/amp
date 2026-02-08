#!/usr/bin/env python
"""Check what parser rules are defined in ampyacc.py"""

import sys
import os

# Read ampyacc.py source
with open('src/ampyacc.py', 'r') as f:
    content = f.read()

# Find all function definitions starting with p_
import re
pattern = r'^def (p_\w+)\('
matches = re.findall(pattern, content, re.MULTILINE)

print("Parser functions found in ampyacc.py:")
for match in matches:
    print(f"  - {match}")

# Check if any JavaScript-related functions exist
js_funcs = [m for m in matches if 'js' in m.lower()]
if js_funcs:
    print(f"\n⚠️  Found {len(js_funcs)} JavaScript-related functions:")
    for func in js_funcs:
        print(f"  - {func}")
else:
    print("\n✓ No JavaScript-related parser functions found")

# Check for parsetab.py
if os.path.exists('src/parsetab.py'):
    print("\n⚠️  Found cached parsetab.py - deleting it...")
    os.remove('src/parsetab.py')
    print("✓ Deleted")
else:
    print("\n✓ No cached parsetab.py found")

if os.path.exists('src/parser.out'):
    print("⚠️  Found cached parser.out - deleting it...")
    os.remove('src/parser.out')
    print("✓ Deleted")
else:
    print("✓ No cached parser.out found")
