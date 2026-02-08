#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from amp import transpile_js_to_py

# Simpler test with AmpScript marker
test_code = '''
try {
    var total = 0;
    for (var i = 0; i < 5; i++) {
        total += i;
    }
    Write("Before marker");
    ###AMPSCRIPT###
    var threshold = 50;
    if (total > threshold) {
        Write("Exceeds");
    } else {
        Write("Within");
    }
} catch(error) {
    Write("Error");
}
'''

print("=== INPUT ===")
print(test_code)

result = transpile_js_to_py(test_code)
print("\n=== OUTPUT ===")
print(result)
