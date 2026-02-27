import re

with open('components/email_verifier.py', 'r') as f:
    text = f.read()

# Instead of relying on exact match which might fail, let's substitute all the CSS
# Wait, let's just use git checkout to revert the CSS back to original first, then apply the Light Glassy theme
