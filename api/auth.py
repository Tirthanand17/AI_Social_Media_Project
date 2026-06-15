from pathlib import Path
import base64
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
USERS = ROOT / "data" / "raw" / "10_users_data.csv"
ROLE_PASSWORDS = {"admin": "admin123", "editor": "editor123", "viewer": "viewer123"}

def load_users():
    return pd.read_csv(USERS)

def login(username, password):
    df = load_users()
    row = df[df["username"].astype(str) == username]
    if row.empty:
        return {"success": False, "message": "Invalid username"}
    user = row.iloc[0].to_dict()
    expected = ROLE_PASSWORDS.get(str(user["role"]).lower(), "password123")
    if password != expected:
        return {"success": False, "message": "Invalid password"}
    payload = {"username": user["username"], "role": user["role"], "brand_name": user["brand_name"]}
    token = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    return {"success": True, "token": token, "user": payload}

def decode_token(token):
    try:
        return json.loads(base64.urlsafe_b64decode(token.encode()).decode())
    except Exception:
        return None

if __name__ == "__main__":
    print(login("admin_techcreate", "admin123"))
