#!/usr/bin/env python
"""Test script that writes output to file"""

import sys
import os

# Delete old parser caches
for f in ['src/parsetab.py', 'src/parser.out']:
    try:
        if os.path.exists(f):
            os.remove(f)
            print(f"Deleted {f}")
    except Exception as e:
        print(f"Error deleting {f}: {e}")

# Import after cache deletion  
from src import amplex, ampyacc, ampcompiler

output = []
output.append("=" * 70)
output.append("PURE AMPSCRIPT TEST")
output.append("=" * 70)

try:
    # Test pure AmpScript
    with open('codesample.ampscript', 'r') as f:
        code = f.read()
    
    output.append(f"\n✓ Read codesample.ampscript ({len(code)} chars)")
    output.append("\nParsing...")
    
    result = ampyacc.parse(code)
    
    if result:
        output.append("✅ PARSE SUCCESS")
        output.append(f"AST: {str(result)[:200]}...")
        
        # Try to compile
        compiler = ampcompiler.AmpCompilerToPy(result)
        compiler.compile()
        output.append("\n✅ COMPILATION SUCCESS")
        
    else:
        output.append("❌ PARSE FAILED - returned None")
        
except Exception as e:
    output.append(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    output.append(traceback.format_exc())

# Write to file
with open('test_results.txt', 'w') as f:
    f.write('\n'.join(output))

print('\n'.join(output))
print("\n\n✓ Results written to test_results.txt")
