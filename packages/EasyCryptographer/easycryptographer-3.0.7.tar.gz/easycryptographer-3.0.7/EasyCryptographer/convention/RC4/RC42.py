import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

while True:
    try:
        key = os.urandom(16)

        cipher = Cipher(algorithms.ARC4(key), mode=None, backend=default_backend())
        encryptor = cipher.encryptor()

        plaintext = input("请输入需要加密的字符(输入q退出): ")
        if plaintext == 'q':
            print("已退出")
            break
        ciphertext = encryptor.update(plaintext.encode('utf-8'))
        print(f"密文: {ciphertext.hex()}")
        print(f"密钥: {key.hex()}\n")

        ciphertext = input("请输入需要解密的字符(输入q退出): ")
        if ciphertext == 'q':
            print("已退出")
            break
        key = input("请输入密钥(输入q退出): ")
        if key == 'q':
            print("已退出")
            break
        cipher_dec = Cipher(algorithms.ARC4(bytes.fromhex(key)), mode=None, backend=default_backend())
        decryptor = cipher_dec.decryptor()

        decrypted = decryptor.update(bytes.fromhex(ciphertext))

        print(f"明文: {decrypted.decode('utf-8')}\n")
    except UnicodeDecodeError:
        print("解密后的数据无法使用UTF-8编码解码, 请检查输入的密钥是否正确\n")
    except ValueError:
        print("无效的密文或密钥\n")
    except Exception as e:
        print(f"未知错误: {str(e)}\n")
