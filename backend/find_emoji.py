import re

with open(r'C:\Users\buimi\OneDrive\Documents\Thực tập\backend\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Common emoji/symbol chars that cause issues
bad_chars = set()
for i, line in enumerate(content.splitlines(), 1):
    for ch in line:
        code = ord(ch)
        # Check for emoji and unusual symbols
        if code > 127:
            # Allow Vietnamese diacritics ( Vietnamese range)
            if not ('\u00c0' <= ch <= '\u1ef3'):
                bad_chars.add((i, ch, code))

if bad_chars:
    print("Found non-Vietnamese unicode chars:")
    for line_num, ch, code in sorted(bad_chars):
        print(f"  Line {line_num}: U+{code:04X} ({ch!r})")
else:
    print("No problematic unicode chars found")
