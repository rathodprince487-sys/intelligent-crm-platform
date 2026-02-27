import re
with open('components/email_verifier.py', 'r') as f:
    c = f.read()

css_block = re.search(r'<style>.*?</style>', c, flags=re.DOTALL)
if css_block:
    print(css_block.group(0))
