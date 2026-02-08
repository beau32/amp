#!/usr/bin/env python
import re

# Test the comment removal with actual comments
test_code = '''<script runat='server' type="text/javascript">
try {
    // JavaScript variables
    var results = [];
    var total = 0;
    // JavaScript loop with complex condition
    for (var i = 0; i < 5; i++) {
        if (i % 2 === 0) {
            Write("Processing even number: " + i);
        } else {
            Write("Processing odd number: " + i);
        }
        total += i;
    }
    Write("Total from JS: " + total);
    
    var threshold = 50;
    if (total > threshold) {
        Write("Exceeds");
    }
}
</script>'''

print("=== ORIGINAL ===")
for i, line in enumerate(test_code.split('\n')):
    print(f"{i:2d}: {line}")

# Remove script tags
py_code = re.sub(r"<script[^>]*>", '', test_code, flags=re.IGNORECASE)
py_code = re.sub(r"</script>", '', py_code, flags=re.IGNORECASE)

# Remove commente
py_code = re.sub(r'//.*?$', '', py_code, flags=re.MULTILINE)

print("\n=== AFTER PROCESSING ===")
for i, line in enumerate(py_code.split('\n')):
    print(f"{i:2d}: {line}")

# Find the for loop
if 'for (var i = 0;' in py_code:
    print("\n FOR LOOP INTACT!")
else:
    print("\nFOR LOOP BROKEN!")
    idx = py_code.find('for (')
    if idx >= 0:
        print(f"Found 'for' at: {py_code[idx:idx+60]}")
