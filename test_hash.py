import hashlib
import json

def _hash_password(password, salt):
    input_enc = password.encode('utf-8')
    salt_enc = salt.encode('utf-8')
    dk = hashlib.pbkdf2_hmac('sha256', input_enc, salt_enc, 100000)
    return dk.hex()

with open("users.json") as f:
    users = json.load(f)

for u in users:
    if u["username"] == "Satyajeet61":
        print(f"Testing passwords for: {u['username']}")
        test_passwords = ["password", "password123", "Satyajeet61", "satyajeet", "admin123", "123456", "Satyajeet@123"]
        for tp in test_passwords:
            if _hash_password(tp, u["salt"]) == u["password_hash"]:
                print(f"FOUND PASSWORD: {tp}")
                break
        else:
            print("Password not found in common list.")
