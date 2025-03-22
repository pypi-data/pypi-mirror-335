import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from publicmodel.common import green_input, orange_print, blue_print, yellow_print, red_print


class CamelliaEncryptionMethod:
    def __init__(self, text):
        self._text = text

    def encryption(self):
        key = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(self._text.encode('utf-8')) + padder.finalize()
        cipher = Cipher(algorithms.Camellia(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data)
        return ciphertext.hex(), key.hex()


class CamelliaDecryptionMethod:
    def __init__(self, text, key):
        self._text = text
        self._key = key

    def decryption(self):
        cipher = Cipher(algorithms.Camellia(bytes.fromhex(self._key)), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(bytes.fromhex(self._text))
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        return plaintext.decode('utf-8')


if __name__ == '__main__':
    while True:
        try:
            plaintext = green_input("请输入需要加密的字符(输入q退出): ")
            if plaintext == 'q':
                orange_print("已退出")
                break

            CEM = CamelliaEncryptionMethod(plaintext)
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
            CDM = CamelliaDecryptionMethod(ciphertext, key)
            decrypted_text = CDM.decryption()
            blue_print(f"明文: {decrypted_text}\n")
        except UnicodeDecodeError:
            red_print("解密后的数据无法使用UTF-8编码解码, 请检查输入的密钥是否正确\n")
        except ValueError:
            red_print("无效的密文或密钥, 请确保输入正确的十六进制字符串\n")
        except Exception:
            red_print("解密失败\n")
