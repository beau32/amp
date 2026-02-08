#!/usr/bin/env python
import re

# Test the script tag removal
test_code = '''<script runat='server' type="text/javascript">
try {
    var total = 0;
    for (var i = 0; i < 5; i++) {
        total += i;
    }
    if (total > threshold) {
        Write("Exceeds");
    }
}
</script>'''

print("=== ORIGINAL ===")
print(test_code)

# Apply script tag removal like transpile does
py_code = re.sub(r"<script[^>]*>", '', test_code, flags=re.IGNORECASE)
py_code = re.sub(r"</script>", '', py_code, flags=re.IGNORECASE)

print("\n=== AFTER SCRIPT TAG REMOVAL ===")
print(py_code)

# Check for loop
if 'for (var i = 0; i < 5' in py_code:
    print("\nFor loop OK!")
else:
    print("\nFor loop BROKEN!")
    if 'threshold' in py_code:
        idx = py_code.find('for')
        print(f"Found 'for' at: {py_code[idx:idx+50]}")
