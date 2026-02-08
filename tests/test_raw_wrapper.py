#!/usr/bin/env python3
"""Debug even simpler: just show what we're starting with."""

import sys
sys.path.insert(0, '..')

with open('codesample_js_advanced.ampscript', 'r') as f:
    data = f.read()

# Simulate what compile_to_python does
wrapper = data
start_delim = '%%['
end_delim = ']%%'

while start_delim in wrapper:
    start_idx = wrapper.find(start_delim)
    end_idx = wrapper.find(end_delim, start_idx)
    if end_idx == -1:
        break
    wrapper = wrapper[:start_idx] + '###AMPSCRIPT###' + wrapper[end_idx + len(end_delim):]

print("=== WRAPPER LINES 10-50 ===")
for i, line in enumerate(wrapper.split('\n')[9:50], 10):
    print(f"Line {i}: {line}")

print("\n=== SEARCH FOR 'for (var i' ===")
for i, line in enumerate(wrapper.split('\n')):
    if 'for (var i' in line:
        print(f"Found at line {i+1} ({i} in 0-indexed):")
        print(f"  EXACT: '{line}'")
        print(f"  Length: {len(line)}")
        print(f"  Repr: {repr(line)}")
