import os
import warnings

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.utils import CryptographyDeprecationWarning
from publicmodel.common import green_input, orange_print, yellow_print, blue_print, red_print

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

while True:
    try:
        key = os.urandom(32)

        cipher = Cipher(algorithms.Blowfish(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()

        plaintext = green_input("请输入需要加密的内容(输入q退出): ")
        if plaintext == 'q':
            orange_print("已退出")
            break
        padder = padding.PKCS7(64).padder()
        padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        yellow_print(f"密文: {ciphertext.hex()}")
        blue_print(f"密钥: {key.hex()}")

        ciphertext = green_input("\n请输入需要解密的内容(输入q退出): ")
        if ciphertext == 'q':
            orange_print("已退出")
            break
        key = green_input("请输入密钥(输入q退出): ")
        if key == 'q':
            orange_print("已退出")
            break

        cipher_dec = Cipher(algorithms.Blowfish(bytes.fromhex(key)), modes.ECB(), backend=default_backend())
        decryptor = cipher_dec.decryptor()

        decrypted_padded = decryptor.update(bytes.fromhex(ciphertext)) + decryptor.finalize()
        unpadder = padding.PKCS7(64).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

        yellow_print(f"明文: {decrypted.decode('utf-8')}\n")
    except ValueError:
        red_print("无效的密文或密钥\n")
    except Exception:
        red_print("解密失败\n")
