import base64
import binascii
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from publicmodel.common import red_print, yellow_print, orange_print, green_input, blue_print


class AESEncryptionMethod:
    def __init__(self, text_arg):
        self._text = text_arg

    def encryption(self):
        key_local = os.urandom(32)
        iv = os.urandom(12)  # 对于GCM模式，推荐使用12字节的随机IV
        cipher = Cipher(algorithms.AES(key_local), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        cipher_text_local = encryptor.update(self._text.encode('utf-8')) + encryptor.finalize()
        last_encrypt_str = base64.b64encode(iv + encryptor.tag + cipher_text_local).decode('utf-8')
        last_encrypt_key = base64.b64encode(key_local).decode('utf-8')
        return last_encrypt_str, last_encrypt_key


class AESDecryptionMethod:
    def __init__(self, text_arg, key_arg):
        self._text = text_arg
        self._key = base64.b64decode(key_arg)

    def decryption(self):
        cipher_text_local = base64.b64decode(self._text.encode('utf-8'))
        iv, tag, cipher_text_local = cipher_text_local[:12], cipher_text_local[12:28], cipher_text_local[28:]
        cipher = Cipher(algorithms.AES(self._key), modes.GCM(iv, tag), backend=default_backend())
        decrypt_local = cipher.decryptor()
        decrypt_text_local = decrypt_local.update(cipher_text_local) + decrypt_local.finalize()
        last_decrypt_str = decrypt_text_local.decode('utf-8')
        return last_decrypt_str


if __name__ == '__main__':
    while True:
        try:
            # 加密
            text = green_input("请输入需要加密的内容(输入q退出): ")
            if text == "q":
                orange_print("已退出")
                break
            encrypt_obj = AESEncryptionMethod(text)
            cipher_text, key = encrypt_obj.encryption()
            blue_print(f"密钥: {key}")
            yellow_print(f"密文: {cipher_text}\n")

            # 解密
            cipher_text = green_input("请输入需要解密的内容(输入q退出): ")
            if cipher_text == "q":
                orange_print("已退出")
                break
            key_input = green_input("请输入密钥(输入q退出): ")
            if key_input == "q":
                orange_print("已退出")
                break
            decrypt_obj = AESDecryptionMethod(cipher_text, key_input)
            plain_text = decrypt_obj.decryption()
            yellow_print(f"明文: {plain_text}\n")
        except TypeError:
            red_print("错误: 无效的密钥, 请输入正确的Base64编码密钥\n")
        except binascii.Error:
            red_print("错误: 密钥长度不正确, 请输入正确的Base64编码密钥\n")
        except InvalidTag:
            red_print("错误: 解密失败, 密钥不正确\n")
        except ValueError:
            red_print("错误: 解密失败, 密文长度不正确\n")
        except Exception as e:
            red_print(f"未知错误: {str(e)}\n")
        except KeyboardInterrupt:
            red_print("\n程序已强制中断")
            break
