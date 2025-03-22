import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from publicmodel.common import green_input, orange_print, blue_print, yellow_print, red_print


def encrypt(plaintext):
    backend = default_backend()
    key = os.urandom(32)
    nonce = os.urandom(16)
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=backend)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext)
    key = f"{key.hex()}+{nonce.hex()}+{str(backend)}"
    return ciphertext.hex(), key


def decrypt(ciphertext, merge_key):
    decompose_text = merge_key.split('+')
    key = decompose_text[0]
    nonce = decompose_text[1]
    backend = decompose_text[2]
    key_bytes = bytes.fromhex(key)
    nonce_bytes = bytes.fromhex(nonce)
    cipher = Cipher(algorithms.ChaCha20(key_bytes, nonce_bytes), mode=None, backend=backend)
    decryptor = cipher.decryptor()
    decrypted_text = decryptor.update(ciphertext)
    return decrypted_text


while True:
    try:
        plaintext = green_input("请输入需要加密的文字(输入q退出): ")
        if plaintext == 'q':
            orange_print("已退出")
            break
        ciphertext, key = encrypt(plaintext.encode('utf-8'))
        blue_print(f"密文: {ciphertext}")
        yellow_print(f"密钥: {key}")
        ciphertext_input = green_input("\n请输入需要解密的文字(输入q退出): ")
        if ciphertext_input == 'q':
            orange_print("已退出")
            break
        key_input = green_input("请输入密钥(输入q退出): ")
        if key_input == 'q':
            orange_print("已退出")
            break
        ciphertext_bytes = bytes.fromhex(ciphertext_input)
        decrypted_text = decrypt(ciphertext_bytes, key_input)
        blue_print(f"明文: {decrypted_text.decode('utf-8')}\n")
    except ValueError:
        red_print("解密失败, 无效的密文或密钥\n")
