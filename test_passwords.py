import sys
import os

# Ensure we're in the right dir
sys.path.insert(0, os.path.abspath("."))
from components.auth import AuthManager

am = AuthManager()
for username in ["admin", "vyonishmomaya@1", "Satyajeet61"]:
    user = am.login(username, "admin123")
    if user:
        print(f"{username}: admin123 (WORKS)")
    else:
        print(f"{username}: Unknown password (WILL RESET TO admin123)")
        am.reset_password("CEO", username, "admin123")
        print(f"{username}: Password reset to admin123")

