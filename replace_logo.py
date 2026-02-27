import base64

html_path = 'websites_showcase.html'
logo_path = 'assets/logo.png'

with open(logo_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

data_uri = f"data:image/png;base64,{b64}"

with open(html_path, 'r') as f:
    content = f.read()

content = content.replace("./assets/logo.png", data_uri)

with open(html_path, 'w') as f:
    f.write(content)

print("Replacement done.")
