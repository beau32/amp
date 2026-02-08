#!/usr/bin/env python3
"""Debug: exact moment of corruption with actual wrapper."""

import re
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

py_code = wrapper

print("=== INITIAL STATE ===")
for_line = [l for l in py_code.split('\n') if 'for (var i =' in l][0]
print(f"FOR LINE: {for_line}")

# Step 1: Remove script tags
print("\n=== STEP 1: Remove script tags ===")
py_code = re.sub(r"<script[^>]*>", '', py_code, flags=re.IGNORECASE)
py_code = re.sub(r"</script>", '', py_code, flags=re.IGNORECASE)
py_code = re.sub(r'<[^>]+>', '', py_code)
for_lines = [l for l in py_code.split('\n') if 'for' in l.lower()]
print(f"Lines with 'for': {len(for_lines)}")
for ln in for_lines[:5]:
    print(f"  {ln}")
