#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from amp import transpile_js_to_py

test_code = '''
for (var i = 0; i < 5; i++) {
    if (i % 2 === 0) {
        Write("even");
    } else {
        Write("odd");
    }
}
Write("Done");
'''

print("=== ORIGINAL ===")
print(test_code)

result = transpile_js_to_py(test_code)
print("\n=== TRANSPILED ===")
print(result)
