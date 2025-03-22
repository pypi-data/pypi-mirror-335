import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from publicmodel.common import green_input, orange_print, blue_print, yellow_print, red_print


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

        plaintext = green_input("请输入需要加密的字符(输入q退出): ")
        if plaintext == 'q':
            orange_print("已退出")
            break

        ciphertext = camellia_encrypt(plaintext.encode('utf-8'), key)
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
        decrypted_text = camellia_decrypt(bytes.fromhex(ciphertext), bytes.fromhex(key))
        blue_print(f"明文: {decrypted_text.decode('utf-8')}\n")
    except UnicodeDecodeError:
        red_print("解密后的数据无法使用UTF-8编码解码, 请检查输入的密钥是否正确\n")
    except ValueError:
        red_print("无效的密文或密钥, 请确保输入正确的十六进制字符串\n")
    except Exception:
        red_print("解密失败\n")
