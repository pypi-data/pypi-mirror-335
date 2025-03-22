import os
import warnings

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.utils import CryptographyDeprecationWarning
from publicmodel.common import green_input, orange_print, blue_print, yellow_print, red_print


class CAST5EncryptionMethod:
    def __init__(self, text):
        self._text = text

    def encryption(self):
        warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
        key = os.urandom(16)
        cipher = Cipher(algorithms.CAST5(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(64).padder()
        padded_plaintext = padder.update(self._text.encode('utf-8')) + padder.finalize()
        ciphertext = encryptor.update(padded_plaintext)
        return ciphertext.hex(), key.hex()


class CAST5DecryptionMethod:
    def __init__(self, text, key):
        self._text = text
        self._key = key

    def decryption(self):
        warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
        cipher_dec = Cipher(algorithms.CAST5(bytes.fromhex(self._key)), modes.ECB(), backend=default_backend())
        decryptor = cipher_dec.decryptor()
        decrypted_padded = decryptor.update(bytes.fromhex(self._text))
        unpadder = padding.PKCS7(64).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        return decrypted.decode('utf-8')


if __name__ == '__main__':
    while True:
        try:
            plaintext = green_input("请输入需要加密的字符(输入q退出): ")
            if plaintext == 'q':
                orange_print("已退出")
                break
            CEM = CAST5EncryptionMethod(plaintext)
            ciphertext, key = CEM.encryption()
            blue_print(f"密文: {ciphertext}")
            yellow_print(f"密钥: {key}\n")

            ciphertext = green_input("请输入需要解密的字符(输入q退出): ")
            if ciphertext == 'q':
                orange_print("已退出")
                break
            key = green_input("请输入密钥(输入q退出): ")
            if key == 'q':
                orange_print("已退出")
                break
            CDM = CAST5DecryptionMethod(ciphertext, key)
            decrypted = CDM.decryption()
            blue_print(f"明文: {decrypted}\n")
        except ValueError:
            red_print("无效的密文或密钥\n")
        except Exception:
            red_print("解密失败\n")
