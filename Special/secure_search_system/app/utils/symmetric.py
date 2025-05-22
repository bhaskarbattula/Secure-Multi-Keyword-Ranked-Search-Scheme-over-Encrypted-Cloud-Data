from cryptography.fernet import Fernet
import os

def generate_key():
    key = Fernet.generate_key()
    with open("secret_key/fernet.key", "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    return open("secret_key/fernet.key", "rb").read()

def encrypt_text_file(file_path, save_path):
    key = load_key()
    fernet = Fernet(key)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    encrypted = fernet.encrypt(content.encode())
    with open(save_path, "wb") as f:
        f.write(encrypted)

def decrypt_text_file(file_path):
    key = load_key()
    fernet = Fernet(key)
    with open(file_path, "rb") as f:
        encrypted = f.read()
    return fernet.decrypt(encrypted).decode()
