#!/usr/bin/env python
import re

code = '''try {
    var total = 0;
    for (var i = 0; i < 5; i++) {
        total += i;
    }
}'''

# First remove var like the transpiler does
code = re.sub(r'\b(var|let|const)\s+', '', code)
print("=== After var removal ===")
print(code)

# Test the for loop regex
pattern = r'\bfor\s*\(([^;]+);([^;]+);([^)]+)\)\s*{'
matches = re.findall(pattern, code)
print(f"\n=== For loop regex matches ===")
print(f"Pattern: {pattern}")
print(f"Matches: {matches}")

# Try the replacement
def replace_for_loop(match):
    init = match.group(1).strip()
    condition = match.group(2).strip()
    increment = match.group(3).strip()
    print(f"Match found: init='{init}', condition='{condition}', increment='{increment}'")
    return f'{init}\nwhile {condition}:\n##LOOP_END_INCREMENT:{increment}##\n##FOR_LOOP_START##'

result = re.sub(pattern, replace_for_loop, code)
print(f"\n=== After for loop replacement ===")
print(result)
