import os
import json
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VAULT_FILE = "vault.enc"
SALT_SIZE = 16

def _derive_key(password: str, salt: bytes) -> bytes:
    """Derives a key from the master password and salt using PBKDF2 HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def is_vault_initialized() -> bool:
    """Checks whether an encrypted vault file already exists on disk."""
    return os.path.exists(VAULT_FILE)

def create_vault(master_password: str, confirm_password: str):
    """Initializes a new encrypted vault file with master password validation."""
    if not master_password:
        return "⚠️ Master password cannot be empty.", False
    if master_password != confirm_password:
        return "❌ Passwords do not match! Please try again.", False
    if len(master_password) < 6:
        return "⚠️ Master password must be at least 6 characters long.", False

    salt = os.urandom(SALT_SIZE)
    key = _derive_key(master_password, salt)
    fernet = Fernet(key)

    # Initialize empty encrypted structure
    initial_data = json.dumps([]).encode()
    encrypted_data = fernet.encrypt(initial_data)

    with open(VAULT_FILE, "wb") as f:
        f.write(salt + encrypted_data)

    return "✅ Vault initialized successfully! Enter your password below to unlock.", True

def unlock_and_display(master_password: str):
    """Decrypts and returns saved vault contents."""
    if not is_vault_initialized():
        return "⚠️ Vault file not found. Create one first.", []

    if not master_password:
        return "⚠️ Enter your master password.", []

    try:
        with open(VAULT_FILE, "rb") as f:
            content = f.read()

        salt = content[:SALT_SIZE]
        encrypted_data = content[SALT_SIZE:]

        key = _derive_key(master_password, salt)
        fernet = Fernet(key)

        decrypted_data = fernet.decrypt(encrypted_data)
        entries = json.loads(decrypted_data.decode())

        rows = [[e["service"], e["username"], e["password"], e["notes"]] for e in entries]
        return "🔓 Vault unlocked successfully!", rows

    except InvalidToken:
        return "❌ Incorrect master password! Access denied.", []
    except Exception as e:
        return f"⚠️ Vault error: {str(e)}", []

def add_entry(service, username, password, notes, master_password):
    """Adds a new entry and re-encrypts the vault."""
    if not is_vault_initialized():
        return "⚠️ Vault file missing. Please create one.", []

    if not master_password:
        return "⚠️ Master password required to save entries.", []

    if not service or not username or not password:
        return "⚠️ Service, Username, and Password fields are required.", []

    try:
        with open(VAULT_FILE, "rb") as f:
            content = f.read()

        salt = content[:SALT_SIZE]
        encrypted_data = content[SALT_SIZE:]

        key = _derive_key(master_password, salt)
        fernet = Fernet(key)

        decrypted_data = fernet.decrypt(encrypted_data)
        entries = json.loads(decrypted_data.decode())

        # Append new record
        entries.append({
            "service": service,
            "username": username,
            "password": password,
            "notes": notes or ""
        })

        # Encrypt and save back
        new_encrypted = fernet.encrypt(json.dumps(entries).encode())
        with open(VAULT_FILE, "wb") as f:
            f.write(salt + new_encrypted)

        rows = [[e["service"], e["username"], e["password"], e["notes"]] for e in entries]
        return "✅ New entry encrypted and saved!", rows

    except InvalidToken:
        return "❌ Incorrect master password! Entry not saved.", []
    except Exception as e:
        return f"⚠️ Save error: {str(e)}", []