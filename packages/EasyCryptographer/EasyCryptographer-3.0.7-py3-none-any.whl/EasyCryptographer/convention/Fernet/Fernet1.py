from cryptography.fernet import Fernet

# 生成秘钥
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# 加密
text = b"hello"
cipher_text = cipher_suite.encrypt(text).decode('utf-8')
print(f"密文: {cipher_text}")

# 解密
plain_text = cipher_suite.decrypt(cipher_text).decode('utf-8')
print(f"明文: {plain_text}")
