from cryptography.fernet import Fernet

while True:
    try:
        # 生成秘钥
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)

        # 加密
        text = input("请输入要加密的内容(输入q退出):")
        if text == 'q':
            print("已退出")
            break
        cipher_text = cipher_suite.encrypt(text.encode('utf-8')).decode('utf-8')
        print(f"密钥: {key.decode('utf-8')}")
        print(f"密文: {cipher_text}\n")

        # 解密
        cipher_text = input("请输入要解密的内容(输入q退出):")
        if cipher_text == 'q':
            print("已退出")
            break
        key_input = input("请输入密钥(输入q退出):")
        if key_input == 'q':
            print("已退出")
            break
        cipher_suite = Fernet(key_input.encode('ascii'))  # 使用用户输入的密钥创建Fernet对象
        plain_text = cipher_suite.decrypt(cipher_text.encode('utf-8')).decode('utf-8')
        print(f"明文: {plain_text}\n")
    except ValueError as v:
        print(f"错误: {v}\n")
