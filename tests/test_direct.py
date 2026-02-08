#!/usr/bin/env python
"""Direct test of AmpScript parsing without PowerShell"""

import sys
import os

# Import modules
from src import amplex, ampyacc

# Read test files
print("=" * 60)
print("Testing Pure AmpScript Parser")
print("=" * 60)

try:
    # Read the pure AmpScript file
    with open('codesample.ampscript', 'r') as f:
        ampscript_code = f.read()
    
    print("\n✓ Successfully read codesample.ampscript")
    print(f"Length: {len(ampscript_code)} characters")
    
    # Parse it
    print("\nParsing...")
    result = ampyacc.parse(ampscript_code)
    
    if result:
        print("\n✅ SUCCESS: Pure AmpScript parsed successfully!")
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
    else:
        print("\n❌ FAILED: Parser returned None")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
