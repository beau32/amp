#!/usr/bin/env python3
"""Debug the exact wrapper being passed to transpile_js_to_py."""

import re

# Read the actual file
with open('codesample_js_advanced.ampscript', 'r') as f:
    data = f.read()

# Simulate what compile_to_python does
wrapper = data
start_delim = '%%['
end_delim = ']%%'

iteration = 0
while start_delim in wrapper:
    iteration += 1
    start_idx = wrapper.find(start_delim)
    end_idx = wrapper.find(end_delim, start_idx)
    if end_idx == -1:
        break
    print(f"\nIteration {iteration}:")
    print(f"  Found AmpScript block from {start_idx} to {end_idx + len(end_delim)}")
    print(f"  Length of block: {end_idx + len(end_delim) - start_idx}")
    wrapper = wrapper[:start_idx] + '###AMPSCRIPT###' + wrapper[end_idx + len(end_delim):]

print(f"\n=== WRAPPER AFTER AMPSCRIPT REPLACEMENT (lines 1-50) ===")
for i, line in enumerate(wrapper.split('\n')[:50], 1):
    print(f"{i:2d}: {line}")

# Now find the for loop in this wrapper
print(f"\n=== SEARCHING FOR FOR LOOP IN WRAPPER ===")
for i, line in enumerate(wrapper.split('\n')):
    if 'for (var' in line:
        print(f"Found at line {i+1}: {line}")
