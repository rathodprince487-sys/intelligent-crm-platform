import re

with open('app.py', 'r') as f:
    text = f.read()

text = re.sub(r'padding-top:\s*[2-9](\.[0-9]+)?rem\s*!important;', 'padding-top: 1rem !important;', text)

with open('app.py', 'w') as f:
    f.write(text)

print("Replaced paddings.")
