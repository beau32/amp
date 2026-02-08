#!/usr/bin/env python
"""Fresh test without import caching"""
import sys
import os

# Force fresh imports
for mod in list(sys.modules.keys()):
    if 'amp' in mod.lower():
        del sys.modules[mod]

# Delete cache files
cache_files = ['src/parsetab.py', 'src/parser.out']
for f in cache_files:
    if os.path.exists(f):
        os.remove(f)
        print(f"Deleted {f}")

# Now import and test
print("\n" + "="*60)
print("Fresh Parser Test - Checking Conflicts")
print("="*60 + "\n")

from src import ampyacc, amplex

# Read codesample.ampscript  
with open('codesample.ampscript', 'r') as f:
    code = f.read()

print(f"Parsing {len(code)} characters of AmpScript...\n")

# Parse
result = ampyacc.parse(code)

if result:
    print("✅ SUCCESS: Parsed successfully")
    print(f"AST root: {result[0] if isinstance(result, tuple) else type(result)}")
else:
    print("❌ FAILED: Parser returned None")

print("\n" + "="*60)
