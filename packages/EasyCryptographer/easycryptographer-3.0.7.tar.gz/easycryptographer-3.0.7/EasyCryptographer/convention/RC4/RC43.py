import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from publicmodel.common import green_input, orange_print, blue_print, yellow_print, red_print

while True:
    try:
        key = os.urandom(16)

        cipher = Cipher(algorithms.ARC4(key), mode=None, backend=default_backend())
        encryptor = cipher.encryptor()

        plaintext = green_input("请输入需要加密的字符(输入q退出): ")
        if plaintext == 'q':
            orange_print("已退出")
            break
        ciphertext = encryptor.update(plaintext.encode('utf-8'))
        blue_print(f"密文: {ciphertext.hex()}")
        yellow_print(f"密钥: {key.hex()}\n")

        ciphertext = green_input("请输入需要解密的字符(输入q退出): ")
        if ciphertext == 'q':
            orange_print("已退出")
            break
        key = green_input("请输入密钥(输入q退出): ")
        if key == 'q':
            orange_print("已退出")
            break
        cipher_dec = Cipher(algorithms.ARC4(bytes.fromhex(key)), mode=None, backend=default_backend())
        decryptor = cipher_dec.decryptor()

        decrypted = decryptor.update(bytes.fromhex(ciphertext))

        blue_print(f"明文: {decrypted.decode('utf-8')}\n")
    except UnicodeDecodeError:
        red_print("无效的密文或密钥\n")
    except ValueError:
        red_print("无效的密文或密钥\n")
    except Exception as e:
        red_print(f"未知错误: {str(e)}\n")
