#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

# Read the advanced sample
with open('codesample_js_advanced.ampscript', 'r') as f:
    data = f.read()

# Simulate what compile_to_python does
# Extract AmpScript blocks
start_delim = '%%['
end_delim = ']%%'
wrapper = data

while start_delim in wrapper:
    start_idx = wrapper.find(start_delim)
    end_idx = wrapper.find(end_delim, start_idx)
    if end_idx == -1:
        break
    wrapper = wrapper[:start_idx] + '###AMPSCRIPT###' + wrapper[end_idx + len(end_delim):]

# Now see what wrapper looks like around the problematic area
lines = wrapper.split('\n')
for i, line in enumerate(lines[8:20], start=8):
    print(f"{i:3d}: {line}")

print("\n=== Looking for for loop ===")
for i, line in enumerate(lines):
    if 'for' in line.lower():
        print(f"{i:3d}: {line}")
