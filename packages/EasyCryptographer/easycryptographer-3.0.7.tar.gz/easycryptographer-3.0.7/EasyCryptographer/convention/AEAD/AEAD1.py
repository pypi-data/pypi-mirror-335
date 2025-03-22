import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

backend = default_backend()


def encrypt(plaintext, key, nonce):
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=backend)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext)
    return ciphertext


def decrypt(ciphertext, key, nonce):
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=backend)
    decryptor = cipher.decryptor()
    decrypted_text = decryptor.update(ciphertext)
    return decrypted_text


key = os.urandom(32)
nonce = os.urandom(16)
plaintext = b'This is a test.'

# 加密
ciphertext = encrypt(plaintext, key, nonce)
print("密文:", ciphertext.hex())
print("密钥:", key.hex())

# 解密
decrypted_text = decrypt(ciphertext, key, nonce)
print("明文:", decrypted_text.decode('utf-8'))
