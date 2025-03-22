import base64
import binascii
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from publicmodel.common import green_input, orange_print, blue_print, yellow_print, red_print


def encrypt(text, key):
    iv = os.urandom(12)  # 对于GCM模式，推荐使用12字节的随机IV
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    cipher_text = encryptor.update(text.encode('utf-8')) + encryptor.finalize()
    return base64.b64encode(iv + encryptor.tag + cipher_text).decode('utf-8')


def decrypt(cipher_text, key):
    cipher_text = base64.b64decode(cipher_text.encode('utf-8'))
    iv, tag, cipher_text = cipher_text[:12], cipher_text[12:28], cipher_text[28:]
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    plain_text = decryptor.update(cipher_text) + decryptor.finalize()
    return plain_text.decode('utf-8')


while True:
    try:
        # 生成密钥
        key = os.urandom(32)

        # 加密
        text = green_input("请输入需要加密的内容(输入q退出): ")
        if text == "q":
            orange_print("已退出")
            break
        cipher_text = encrypt(text, key)
        blue_print(f"密钥: {base64.b64encode(key).decode('utf-8')}")
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
        plain_text = decrypt(cipher_text, base64.b64decode(key_input))
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
