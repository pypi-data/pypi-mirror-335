import os
import warnings

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.utils import CryptographyDeprecationWarning

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

while True:
    try:
        key = os.urandom(16)

        cipher = Cipher(algorithms.CAST5(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()

        plaintext = input("请输入需要加密的字符(输入q退出):")
        if plaintext == 'q':
            print("已退出")
            break

        padder = padding.PKCS7(64).padder()
        padded_plaintext = padder.update(plaintext.encode('utf-8')) + padder.finalize()

        ciphertext = encryptor.update(padded_plaintext)
        print(f"密文: {ciphertext.hex()}")
        print(f"密钥: {key.hex()}\n")

        ciphertext = input("请输入需要解密的密文(输入q退出):")
        if ciphertext == 'q':
            print("已退出")
            break
        key = input("请输入密钥(输入q退出):")
        if key == 'q':
            print("已退出")
            break
        cipher_dec = Cipher(algorithms.CAST5(bytes.fromhex(key)), modes.ECB(), backend=default_backend())
        decryptor = cipher_dec.decryptor()
        decrypted_padded = decryptor.update(bytes.fromhex(ciphertext))

        unpadder = padding.PKCS7(64).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

        print(f"明文: {decrypted.decode('utf-8')}\n")
    except ValueError:
        print("无效的密文或密钥\n")
    except Exception:
        print("解密失败\n")
