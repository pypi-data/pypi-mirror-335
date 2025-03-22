from cryptography.fernet import Fernet, InvalidToken
from publicmodel.common import green_input, orange_print, yellow_print, red_print, blue_print

while True:
    try:
        # 生成秘钥
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)

        # 加密
        text = green_input("请输入要加密的内容(输入q退出): ")
        if text == 'q':
            orange_print("已退出")
            break
        cipher_text = cipher_suite.encrypt(text.encode('utf-8')).decode('utf-8')
        blue_print(f"密钥: {key.decode('utf-8')}")
        yellow_print(f"密文: {cipher_text}\n")

        # 解密
        cipher_text = green_input("请输入要解密的内容(输入q退出): ")
        if cipher_text == 'q':
            orange_print("已退出")
            break
        key_input = green_input("请输入密钥(输入q退出): ")
        if key_input == 'q':
            orange_print("已退出")
            break
        cipher_suite = Fernet(key_input.encode('ascii'))  # 使用用户输入的密钥创建Fernet对象
        plain_text = cipher_suite.decrypt(cipher_text.encode('utf-8')).decode('utf-8')
        yellow_print(f"明文: {plain_text}\n")
    except ValueError:
        red_print("错误: 无效的密钥, 请输入32个URL安全的base64编码字节\n")
    except InvalidToken:
        red_print("错误: 解密失败, 密钥或密文无效\n")
    except KeyboardInterrupt:
        red_print("\n程序已强制中断")
        break
