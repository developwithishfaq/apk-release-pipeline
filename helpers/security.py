from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode
import os

key = b"0123456789abcdef0123456789abcdef"  # 32 bytes for AES-256
iv = b"abcdef9876543210"                   # 16 bytes for AES block size

def encrypt_string(plain_text: str) -> str:
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(plain_text.encode()) + encryptor.finalize()
    return b64encode(encrypted).decode('utf-8')

def decrypt_string(encrypted_text: str) -> str:
    encrypted_data = b64decode(encrypted_text)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
    return decrypted.decode('utf-8')