from cryptography.fernet import Fernet
import os

# Make sure the secret_key folder exists
os.makedirs("secret_key", exist_ok=True)

# Generate and save the key
key = Fernet.generate_key()
with open("secret_key/fernet.key", "wb") as f:
    f.write(key)

print("✅ Fernet key generated and saved successfully!")
