import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

# 生成密钥和nonce
key = os.urandom(32)
nonce = os.urandom(16)

# 创建cipher
cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())


# 加密
def encrypt(data, cipher):
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data)
    return encrypted_data


# 解密
def decrypt(encrypted_data, cipher):
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data)
    return decrypted_data


data = b"Hello, world!"
encrypted_data = encrypt(data, cipher)
print("密文:", encrypted_data)

decrypted_data = decrypt(encrypted_data, cipher)
print("明文:", decrypted_data)
