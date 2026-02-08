#!/usr/bin/env python
import re

# Test the comment removal regex
test_code = '''for (var i = 0; i < 5; i++) {
    total += i;
}
if (total > threshold) {
    Write("Exceeds");
}'''

print("=== ORIGINAL ===")
print(test_code)

# Apply comment removal
result = re.sub(r'//.*?$', '', test_code, flags=re.MULTILINE)
print("\n=== AFTER COMMENT REMOVAL ===")
print(result)

# Check if they're the same
if result == test_code:
    print("\nComment removal had NO EFFECT (correct!)")
else:
    print("\nComment removal CHANGED THE CODE!")
