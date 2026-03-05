import re

with open("components/analytics.py", "r") as f:
    content = f.read()

content = content.replace(
    "[data-testid=\"stAppViewContainer\"] * { font-family: 'Inter', sans-serif !important; }",
    "[data-testid=\"stAppViewContainer\"] *:not([translate=\"no\"]):not(svg):not([class*=\"material\"]):not([icon]) { font-family: 'Inter', sans-serif !important; }"
)

with open("components/analytics.py", "w") as f:
    f.write(content)
