#!/usr/bin/env python

# Security-related scripts, such as password hashing and unencryption.

from argon2 import PasswordHasher
import jwt # Specifically PyJWT, not JWT; Generates JSON Web Tokens (session keys)
import secrets # Base keys for JWT to generate JSON Web Tokens
import uuid # Random token ids
from datetime import datetime, timezone, timedelta # JWT Session Key expiry
from pathlib import Path

# ----------
# Finds the version

version = ""
# 1. Find the absolute path to this script
script_dir = Path(__file__).resolve().parent
# 2. Go up one directory and points to the version file
target_file = script_dir.parent / "version.txt"

try:
    with open(target_file, "r") as file:
        version = file.read().strip()
except Exception:
    version = "*UNKNOWN"

# ----------
# Passwords

ph = PasswordHasher() # Set up the password hasher

def hashpassword(raw_password):
    hashed_password = ph.hash(raw_password)
    return hashed_password

def checkpassword(raw_password, hashed_password):
    try:
        ph.verify(hashed_password, raw_password) # Gets argon2 to auto check it
        return True
    except Exception: # An error occurs, USUALLY an incorrect password
        return False



# ----------
# JWT
SECRET_KEY = secrets.token_hex(32) # TODO: make the secret permanent via os.getenv

def generateJWT(JWT_UUID, JWT_Username):
    payload = {
        "iss": "StudyNet", # Issuer
        "version": str(version), # Custom field - version (To ensure that the user can not relogin if the backend updates, to prevent edge case errors)
        "sub": str(JWT_UUID), # Subject (uuid)
        "username": str(JWT_Username), # Custom field - username
        "exp": datetime.now(timezone.utc) + timedelta(hours=24), # Expires in
        "iat": datetime.now(timezone.utc), # Issued at
        "jti": f"{uuid.uuid7()}" # JWT ID - specifically, a random string (uuid). UUID 7 allows for tracking in db with a timer, preserving storage space for people with many logged in sessions at once. TODO: in db, code so that using the given exp, autoexpire the jti once the time is up. This will also be useful for "Log me out on all devices"
    }

    # Generates the JWT, and returns it
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {"token": token, "jti": payload["jti"]} # EXP field is not NEEDED given the fact that JTI uses UUID7.

def decodeJWT(key):
    pass