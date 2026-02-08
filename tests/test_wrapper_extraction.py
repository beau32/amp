#!/usr/bin/env python3
"""Debug the wrapper/marker extraction."""

# Read file
with open('codesample_js_advanced.ampscript', 'r') as f:
    content = f.read()

# Print full content first 60 lines to see if markup is right
print("=== FULL CONTENT (lines 1-60) ===")
for i, line in enumerate(content.split('\n')[:60], 1):
    print(f"{i:2d}: {line}")

# Now check what the compile_to_python function does
print("\n=== CHECKING WRAPPER EXTRACTION ===")

# Pattern: %%[ ... ]%%
import re

# Find all AmpScript blocks
ampscript_blocks = []
wrapper_text = content
for match in re.finditer(r'%%\[[\s\S]*?\]%%', content):
    ampscript_blocks.append(match.group(0))
    print(f"Found AmpScript block at {match.start()}-{match.end()}: {len(match.group(0))} chars")
    print(f"  First 50 chars: {match.group(0)[:50]}")

# Now replace with markers
wrapper_replaced = content
for i, block in enumerate(ampscript_blocks):
    wrapper_replaced = wrapper_replaced.replace(block, f'###AMPSCRIPT_BLOCK_{i}###', 1)

print("\n=== WRAPPER AFTER REPLACEMENT (first 50 lines) ===")
for i, line in enumerate(wrapper_replaced.split('\n')[:50], 1):
    print(f"{i:2d}: {line}")
