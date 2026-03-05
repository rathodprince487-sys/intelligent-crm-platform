from PIL import Image
import base64
import re
import sys

try:
    img = Image.open('assets/logo.png').convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        r, g, b, a = item
        # If the pixel is close to white, make it transparent
        if r > 200 and g > 200 and b > 200:
            newData.append((255, 255, 255, 0))
        else:
            newData.append((0, 0, 0, 255)) # Make the logo black for the mask

    img.putdata(newData)
    img.save('assets/logo_transparent.png', 'PNG')

    with open('assets/logo_transparent.png', 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')

    html_path = 'websites_showcase.html'
    with open(html_path, 'r') as f:
        content = f.read()

    new_content = re.sub(r"url\('data:image/png;base64,[^']+'\)", f"url('data:image/png;base64,{b64}')", content)

    with open(html_path, 'w') as f:
        f.write(new_content)
    print("Done making transparent mask and injecting!")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
