import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


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
    # 生成密钥
    key = os.urandom(32)

    # 加密
    text = input("请输入需要加密的内容(输入q退出): ")
    if text == "q":
        print("已退出")
        break
    cipher_text = encrypt(text, key)
    print(f"密钥: {base64.b64encode(key).decode('utf-8')}")
    print(f"密文: {cipher_text}\n")

    # 解密
    cipher_text = input("请输入需要解密的内容(输入q退出): ")
    if cipher_text == "q":
        print("已退出")
        break
    key_input = input("请输入密钥(输入q退出): ")
    if key_input == "q":
        print("已退出")
        break
    plain_text = decrypt(cipher_text, base64.b64decode(key_input))
    print(f"明文: {plain_text}\n")
