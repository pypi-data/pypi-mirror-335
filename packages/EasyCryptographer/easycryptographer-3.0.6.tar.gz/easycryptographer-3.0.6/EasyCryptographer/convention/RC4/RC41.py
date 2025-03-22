import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

# 生成一个密钥
key = os.urandom(16)

# 创建一个加密对象
cipher = Cipher(algorithms.ARC4(key), mode=None, backend=default_backend())
encryptor = cipher.encryptor()

# 加密数据
plaintext = "Hello, world!"
ciphertext = encryptor.update(plaintext.encode('utf-8'))
print(f"密文: {ciphertext.hex()}")
print(f"密钥: {key.hex()}")

# 创建一个解密对象
cipher_dec = Cipher(algorithms.ARC4(key), mode=None, backend=default_backend())
decryptor = cipher_dec.decryptor()

# 解密数据
decrypted = decryptor.update(ciphertext)

print(f"明文: {decrypted.decode('utf-8')}")
