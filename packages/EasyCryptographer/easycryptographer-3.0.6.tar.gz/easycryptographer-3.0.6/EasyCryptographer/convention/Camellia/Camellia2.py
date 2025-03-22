import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def camellia_encrypt(plaintext, key):
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.Camellia(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data)
    return ciphertext


def camellia_decrypt(ciphertext, key):
    cipher = Cipher(algorithms.Camellia(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext)
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()
    return plaintext


while True:
    try:
        key = os.urandom(16)

        plaintext = input("请输入需要加密的字符(输入q退出): ")
        if plaintext == 'q':
            print("已退出")
            break

        ciphertext = camellia_encrypt(plaintext.encode('utf-8'), key)
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
        decrypted_text = camellia_decrypt(bytes.fromhex(ciphertext), bytes.fromhex(key))
        print(f"明文: {decrypted_text.decode('utf-8')}\n")
    except UnicodeDecodeError:
        print("解密后的数据无法使用UTF-8编码解码, 请检查输入的密钥是否正确\n")
    except ValueError:
        print("无效的密文或密钥, 请确保输入正确的十六进制字符串\n")
    except Exception:
        print("解密失败\n")
