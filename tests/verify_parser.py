"""Verify parser generation and conflict count"""
import sys
import os
import io
from contextlib import redirect_stderr

# Clear caches
for mod in list(sys.modules.keys()):
    if 'amp' in mod.lower():
        del sys.modules[mod]

for f in ['src/parsetab.py', 'src/parser.out']:
    if os.path.exists(f):
        os.remove(f)

print("="*60)
print("Parser Generation Test")
print("="*60)

# Capture stderr to count warnings
stderr_capture = io.StringIO()

with redirect_stderr(stderr_capture):
    from src import ampyacc

stderr_output = stderr_capture.getvalue()

# Count conflicts
shift_reduce = stderr_output.count("shift/reduce conflict")
reduce_reduce = stderr_output.count("reduce/reduce conflict")

print(f"\n✓ Parser generated successfully")
print(f"\nConflict Summary:")
print(f"  - Shift/Reduce conflicts: {shift_reduce}")
print(f"  - Reduce/Reduce conflicts: {reduce_reduce}")

if shift_reduce == 0 and reduce_reduce == 0:
    print(f"\n🎉 SUCCESS: NO CONFLICTS!")
elif shift_reduce <= 2 and reduce_reduce == 0:
    print(f"\n✓ Acceptable: Only {shift_reduce} shift/reduce conflicts (common with LALR grammars)")
else:
    print(f"\n⚠️  Warning: Grammar has conflicts that should be resolved")

print("\n" + "="*60)
