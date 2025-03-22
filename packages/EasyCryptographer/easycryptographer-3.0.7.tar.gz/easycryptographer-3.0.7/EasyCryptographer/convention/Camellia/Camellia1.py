import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def camellia_encrypt(plaintext, key):
    padder = padding.PKCS7(128).padder()  # 128 is block size for Camellia
    padded_data = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.Camellia(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data)
    return ciphertext


def camellia_decrypt(ciphertext, key):
    cipher = Cipher(algorithms.Camellia(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext)
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()
    return plaintext


# 生成一个16字节的随机密钥
key = os.urandom(16)

# 输入需要加密的文本
plaintext = b"Hello, World! This is a test."

# 使用Camellia加密
ciphertext = camellia_encrypt(plaintext, key)
print("密文:", ciphertext.hex())
print("密钥:", key.hex())

# 使用Camellia解密
decrypted_text = camellia_decrypt(ciphertext, key)
print("明文:", decrypted_text.decode('utf-8'))
