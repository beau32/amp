#!/usr/bin/env python3
"""Debug transpile_js_to_py step by step to find corruption."""

import sys
import os
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Not needed for this test - we'll just test the transformations directly

# Now let's manually walk through the transformations
test_code = """<script runat='server' type="text/javascript">
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
</script>"""

# Simulate the transpile_js_to_py function transformations manually
print("=== ORIGINAL ===")
print(test_code)
print("\n=== STEP 1: Remove script tags ===")
step1 = re.sub(r'</?script[^>]*>', '', test_code)
print(step1)

print("\n=== STEP 2: Remove JS comments ===")
step2 = re.sub(r'//.*?$', '', step1, flags=re.MULTILINE)
print(step2)

print("\n=== STEP 3: Replace try-catch (before brace) ===")
# More permissive try-catch pattern
step3 = re.sub(r'try\s*\{', 'try:', step2)
step3 = re.sub(r'\}\s*catch\s*\(([^)]+)\)\s*\{', 'except Exception as \\1:', step3)
print(step3)

print("\n=== STEP 4: Replace for loops ===")
# Store original for loop replacement regex
for_loop_pattern = r'for\s*\(\s*var\s+(\w+)\s*=\s*([^;]+);\s*([^;]+);\s*([^)]+)\)\s*\{'

matches = list(re.finditer(for_loop_pattern, step3))
print(f"Found {len(matches)} for loops")
for i, match in enumerate(matches):
    print(f"  Loop {i}: var={match.group(1)}, init={match.group(2)}, cond={match.group(3)}, incr={match.group(4)}")
    print(f"  Full match: {match.group(0)}")

step4 = re.sub(for_loop_pattern, 
              lambda m: f"{m.group(1)} = {m.group(2)}\n        while {m.group(3)}:\n            ##FOR_LOOP_START##{m.group(1)}##END_FOR_LOOP##", 
              step3)
print("\nAfter FOR replacement:")
print(step4)

print("\n=== STEP 5: Replace while loops ===")
step5 = re.sub(r'while\s*\(([^)]+)\)\s*\{', r'while \1:', step4)
print(step5)
