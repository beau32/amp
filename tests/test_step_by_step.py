#!/usr/bin/env python3
"""Debug the exact moment when for loop gets corrupted."""

import re

# Simulate the wrapper with markers
# Read the actual wrapper from the transpilation
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
step = 0

# Step 1: Remove script tags
step += 1
py_code = re.sub(r"<script[^>]*>", '', py_code, flags=re.IGNORECASE)
py_code = re.sub(r"</script>", '', py_code, flags=re.IGNORECASE)
py_code = re.sub(r'<[^>]+>', '', py_code)
print(f"Step {step}: After script tag removal")
if 'for (var i =' in py_code:
    for_line = [ln for ln in py_code.split('\n') if 'for (var i =' in ln][0]
    print(f"  FOR LINE: {for_line}")

# Step 2: Remove comments  
step += 1
py_code = re.sub(r'//.*?$', '', py_code, flags=re.MULTILINE)
py_code = re.sub(r'/\*[\s\S]*?\*/', '', py_code)
print(f"Step {step}: After comment removal")
if 'for (var i =' in py_code:
    for_line = [ln for ln in py_code.split('\n') if 'for (var i =' in ln][0]
    print(f"  FOR LINE: {for_line}")

# Step 3: Replace try-catch
step += 1
py_code = re.sub(r'\btry\s*\{', 'try:', py_code)
py_code = re.sub(r'\}\s*catch\s*\(([^)]*)\)\s*\{', r'except Exception as \1:', py_code)
print(f"Step {step}: After try-catch replacement")
if 'for (var i =' in py_code:
    for_line = [ln for ln in py_code.split('\n') if 'for (var i =' in ln][0]
    print(f"  FOR LINE: {for_line}")
else:
    print("  FOR LINE: NOT FOUND - already corrupted!")

# Step 4: Replace for loops
step += 1
def replace_for_loop(match):
    init = match.group(1).strip()
    condition = match.group(2).strip()
    increment = match.group(3).strip()
    
    if '++' in increment:
        var = increment.replace('++', '').strip()
        py_increment = f'{var} += 1'
    elif '--' in increment:
        var = increment.replace('--', '').strip()
        py_increment = f'{var} -= 1'
    elif '+=' in increment or '-=' in increment:
        py_increment = increment
    else:
        py_increment = increment
    
    return f'{init}\nwhile {condition}:\n##LOOP_END_INCREMENT:{py_increment}##\n##FOR_LOOP_START##'

print(f"Step {step} starting: Before FOR loop replacement")
print("  Checking for for-loop pattern matches...")
matches = list(re.finditer(r'\bfor\s*\(([^;]+);([^;]+);([^)]+)\)\s*\{', py_code))
print(f"  Found {len(matches)} matches")
for i, m in enumerate(matches):
    print(f"    Match {i}: init={m.group(1)}, cond={m.group(2)}, incr={m.group(3)}")

py_code = re.sub(r'\bfor\s*\(([^;]+);([^;]+);([^)]+)\)\s*{', replace_for_loop, py_code)
print(f"After FOR replacement")
for_lines = [ln for ln in py_code.split('\n') if 'while' in ln or 'for' in ln or 'i =' in ln]
print(f"  Lines with for/while/assignment:")
for ln in for_lines[:10]:
    print(f"    {ln}")

# Step 5: Replace while loops
step += 1
py_code = re.sub(r'\bwhile\s*\(([^)]*)\)\s*\{', r'while \1:', py_code)
print(f"Step {step}: After while replacement")
for_lines = [ln for ln in py_code.split('\n') if 'while' in ln or 'for' in ln]
for ln in for_lines[:10]:
    print(f"  {ln}")

# Step 6: Replace if statements
step += 1
py_code = re.sub(r'\bif\s*\(([^)]*)\)\s*\{', r'if \1:', py_code)
py_code = re.sub(r'}\s*else\s*if\s*\(([^)]*)\)\s*\{', r'elif \1:', py_code)
py_code = re.sub(r'}\s*else\s*\{', 'else:', py_code)
print(f"Step {step}: After if replacement")
for_lines = [ln for ln in py_code.split('\n') if 'for' in ln or 'if' in ln or 'while' in ln]
for ln in for_lines[:10]:
    print(f"  {ln}")

# Step 7: Remove braces
step += 1
py_code = py_code.replace('{', '')
py_code = py_code.replace('}', '')
print(f"Step {step}: After brace removal")
for i, ln in enumerate(py_code.split('\n')):
    if any(kw in ln for kw in ['for', 'while', 'if', 'var i']):
        print(f"  Line {i}: {ln}")
