from cryptography.fernet import Fernet
import numpy as np
import os
from dotenv import load_dotenv
import base64, json

class TreeNode:
    def __init__(self, vector, fid=None):
        self.vector = vector
        self.fid = fid
        self.left = None
        self.right = None

load_dotenv()

def get_encryption_key():
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        key = Fernet.generate_key().decode()
        # Warning to set this in production
    return key.encode()




# Master key (store this in environment variables in production!)
MASTER_KEY = Fernet.generate_key()  # Or: os.getenv('MASTER_KEY').encode()

def encrypt_key(key: np.ndarray) -> str:
    """Encrypt numpy array key for storage"""
    cipher_suite = Fernet(MASTER_KEY)
    return cipher_suite.encrypt(key.tobytes()).decode()

def decrypt_key(encrypted_key: str) -> np.ndarray:
    """Decrypt key for usage"""
    cipher_suite = Fernet(MASTER_KEY)
    return np.frombuffer(cipher_suite.decrypt(encrypted_key.encode()))


import numpy as np
from cryptography.fernet import Fernet

def encrypt_array(key_array: np.ndarray) -> str:
    """Encrypt numpy array with shape preservation"""
    cipher_suite = Fernet(MASTER_KEY)
    # Store both data and shape
    payload = {
        'data': key_array.tobytes(),
        'dtype': str(key_array.dtype),
        'shape': key_array.shape
    }
    return cipher_suite.encrypt(json.dumps(payload).encode()).decode()

def decrypt_array(encrypted: str) -> np.ndarray:
    """Decrypt numpy array with original shape"""
    cipher_suite = Fernet(MASTER_KEY)
    decrypted = json.loads(cipher_suite.decrypt(encrypted.encode()).decode())
    return np.frombuffer(
        decrypted['data'].encode('latin1'),  # Convert back to bytes
        dtype=np.dtype(decrypted['dtype'])
    ).reshape(decrypted['shape'])



def generate_key():
    """Generate a secure key using Fernet encryption."""
    return Fernet.generate_key()


from cryptography.fernet import Fernet
import base64

def encrypt_text_file(input_path, output_path, key):
    """Encrypt a file using Fernet"""
    try:
        fernet = Fernet(key)
        with open(input_path, 'rb') as f:
            data = f.read()
        encrypted = fernet.encrypt(data)
        with open(output_path, 'wb') as f:
            f.write(encrypted)
        return True
    except Exception as e:
        print(f"Encryption failed: {str(e)}")
        return False

def decrypt_text_file(file_path, key):
    """Decrypt a file using Fernet"""
    try:
        fernet = Fernet(key)
        with open(file_path, 'rb') as f:
            encrypted = f.read()
        return fernet.decrypt(encrypted).decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        return None

def generate_secret_key(m):
    """Generate a secret key with size m for encryption (used for tree encryption)."""
    S = np.random.randint(0, 2, m)
    M1 = np.random.rand(m, m)
    M2 = np.random.rand(m, m)
    return S, M1, M2


def encrypt_vector(vector, S, M1, M2):
    """Encrypt a vector using the provided secret key matrices."""
    v1, v2 = np.zeros_like(vector), np.zeros_like(vector)
    for i in range(len(vector)):
        if S[i] == 0:
            v1[i] = v2[i] = vector[i]
        else:
            rand = np.random.rand()
            v1[i], v2[i] = rand, vector[i] - rand
    return M1.T @ v1, M2.T @ v2


def encrypt_tree(root, S, M1, M2):
    """Recursively encrypt the tree using secret key matrices."""
    if root is None:
        return None
    enc1, enc2 = encrypt_vector(root.vector, S, M1, M2)
    root.vector = (enc1, enc2)
    root.left = encrypt_tree(root.left, S, M1, M2)
    root.right = encrypt_tree(root.right, S, M1, M2)
    return root