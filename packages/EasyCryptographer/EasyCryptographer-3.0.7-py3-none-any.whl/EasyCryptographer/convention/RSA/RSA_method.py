import binascii
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from publicmodel.common import green_input, red_print, orange_print, blue_print, yellow_print


class RSAEncryptionMethod:
    def __init__(self, text):
        self._text = text

    def encryption(self):
        key = os.urandom(32)
        nonce = os.urandom(16)
        cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(self._text.encode("utf-8"))
        key = f"{binascii.hexlify(key).decode()}+{binascii.hexlify(nonce).decode()}"
        return binascii.hexlify(encrypted_data).decode(), key


class RSADecryptionMethod:
    def __init__(self, text, key):
        self._text = text
        self._key = key

    def decryption(self):
        key_input, nonce_input = self._key.split("+")
        cipher_text = binascii.unhexlify(self._text)
        key_input = binascii.unhexlify(key_input)
        nonce_input = binascii.unhexlify(nonce_input)
        cipher_input = Cipher(algorithms.ChaCha20(key_input, nonce_input), mode=None, backend=default_backend())
        decryptor = cipher_input.decryptor()
        decrypted_data = decryptor.update(cipher_text)
        return decrypted_data.decode('utf-8')


if __name__ == "__main__":
    while True:
        try:
            text = green_input("请输入要加密的内容(输入q退出): ")
            if text == "q":
                orange_print("已退出")
                break
            REM = RSAEncryptionMethod(text)
            cipher_text, key = REM.encryption()
            blue_print(f"密文: {cipher_text}")
            yellow_print(f"密钥: {key}\n")

            cipher_text = green_input("请输入要解密的内容(输入q退出): ")
            if cipher_text == 'q':
                orange_print("已退出")
                break
            key = green_input("请输入密钥(输入q退出): ")
            if key == 'q':
                orange_print("已退出")
                break
            RDM = RSADecryptionMethod(cipher_text, key)
            plain_text = RDM.decryption()
            blue_print(f"明文: {plain_text}\n")
        except UnicodeDecodeError:
            red_print("解密后的数据无法使用UTF-8编码解码, 请检查输入的密钥是否正确\n")
        except ValueError:
            red_print("输入的密钥或密文不正确\n")
