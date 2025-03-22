import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from publicmodel.common import green_input, orange_print, blue_print, yellow_print, red_print


class RC4EncryptionMethod:
    def __init__(self, text):
        self._text = text

    def encryption(self):
        key = os.urandom(16)
        cipher = Cipher(algorithms.ARC4(key), mode=None, backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(self._text.encode('utf-8'))
        return ciphertext.hex(), key.hex()


class RC4DecryptionMethod:
    def __init__(self, text, key):
        self._text = text
        self._key = key

    def decryption(self):
        cipher_dec = Cipher(algorithms.ARC4(bytes.fromhex(self._key)), mode=None, backend=default_backend())
        decryptor = cipher_dec.decryptor()
        decrypted = decryptor.update(bytes.fromhex(self._text))
        return decrypted.decode('utf-8')


if __name__ == '__main__':
    while True:
        try:
            plaintext = green_input("请输入需要加密的字符(输入q退出): ")
            if plaintext == 'q':
                orange_print("已退出")
                break
            REM = RC4EncryptionMethod(plaintext)
            ciphertext, key = REM.encryption()
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
            RDM = RC4DecryptionMethod(ciphertext, key)
            decrypted = RDM.decryption()
            blue_print(f"明文: {decrypted}\n")
        except UnicodeDecodeError:
            red_print("无效的密文或密钥\n")
        except ValueError:
            red_print("无效的密文或密钥\n")
        except Exception as e:
            red_print(f"未知错误: {str(e)}\n")
