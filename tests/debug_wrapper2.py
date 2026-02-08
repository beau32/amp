#!/usr/bin/env python
# Check what wrapper looks like with AmpScript replacement

data = '''
try {
    var total = 0;
    for (var i = 0; i < 5; i++) {
        total += i;
    }
    Write("Before marker");
    %%[
    VAR @count = 10
    ]%%
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

# Simulate the wrapper replacement
wrapper = data
start_delim = '%%['
end_delim = ']%%'

while start_delim in wrapper:
    start_idx = wrapper.find(start_delim)
    end_idx = wrapper.find(end_delim, start_idx)
    if end_idx == -1:
        break
    wrapper = wrapper[:start_idx] + '###AMPSCRIPT###' + wrapper[end_idx + len(end_delim):]

print("=== WRAPPER RESULT ===")
for_idx = wrapper.find('for (')
if for_idx >= 0:
    print(wrapper[max(0, for_idx-100):for_idx+200])
else:
    print("NO FOR LOOP FOUND")
