import binascii
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from publicmodel.common import green_input, orange_print, blue_print, yellow_print, red_print

# 生成密钥和nonce
key = os.urandom(32)
nonce = os.urandom(16)

# 创建cipher
cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())


# 加密
def encrypt(data, cipher):
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data)
    return encrypted_data


# 解密
def decrypt(encrypted_data, cipher):
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data)
    return decrypted_data


while True:
    step = 0
    try:
        data = green_input("请输入要加密的内容(输入q退出): ")
        if data == "q":
            orange_print("已退出")
            break
        encrypted_data = encrypt(data.encode("utf-8"), cipher)
        blue_print(f"密文: {binascii.hexlify(encrypted_data).decode()}")
        yellow_print(f"密钥: {binascii.hexlify(key).decode()}+{binascii.hexlify(nonce).decode()}\n")

        cipher_text = green_input("请输入要解密的内容(输入q退出): ")
        if cipher_text == 'q':
            orange_print("已退出")
            break
        key_nonce_input = green_input("请输入密钥(输入q退出): ")
        if key_nonce_input == 'q':
            orange_print("已退出")
            break
        key_input, nonce_input = key_nonce_input.split("+")
        step += 1
        cipher_text = binascii.unhexlify(cipher_text)
        step += 1
        key_input = binascii.unhexlify(key_input)
        nonce_input = binascii.unhexlify(nonce_input)
        cipher_input = Cipher(algorithms.ChaCha20(key_input, nonce_input), mode=None, backend=default_backend())
        decrypted_data = decrypt(cipher_text, cipher_input)
        blue_print(f"明文: {decrypted_data.decode('utf-8')}\n")
    except UnicodeDecodeError:
        red_print("解密后的数据无法使用UTF-8编码解码, 请检查输入的密钥是否正确\n")
    except ValueError:
        if step == 0 or step == 2:
            red_print("输入的密钥不正确\n")
        else:
            red_print("输入的密文不正确\n")
