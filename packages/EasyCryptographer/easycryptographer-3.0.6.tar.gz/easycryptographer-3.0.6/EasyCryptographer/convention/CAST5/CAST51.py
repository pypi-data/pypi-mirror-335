import os
import warnings

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.utils import CryptographyDeprecationWarning

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# 生成一个密钥
key = os.urandom(16)

# 创建一个加密对象
cipher = Cipher(algorithms.CAST5(key), modes.ECB(), backend=default_backend())
encryptor = cipher.encryptor()

# 加密数据（注意：CAST5需要8字节的倍数）
plaintext = "Hello, world!123"
ciphertext = encryptor.update(plaintext.encode('utf-8'))
print("密文:", ciphertext.hex())

# 创建一个解密对象
cipher_dec = Cipher(algorithms.CAST5(key), modes.ECB(), backend=default_backend())
decryptor = cipher_dec.decryptor()

# 解密数据
decrypted = decryptor.update(ciphertext)

print("明文:", decrypted.decode('utf-8'))
