import json
import hashlib
import secrets

def _hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    input_enc = password.encode('utf-8')
    salt_enc = salt.encode('utf-8')
    dk = hashlib.pbkdf2_hmac('sha256', input_enc, salt_enc, 100000)
    return dk.hex(), salt

with open("users.json", "r") as f:
    users = json.load(f)

for u in users:
    if u["username"] == "Satyajeet61":
        ph, salt = _hash_password("admin123")
        u["password_hash"] = ph
        u["salt"] = salt
        print("Password reset to 'admin123'")

with open("users.json", "w") as f:
    json.dump(users, f, indent=4)
