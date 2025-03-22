from cryptography.fernet import Fernet, InvalidToken
from publicmodel.common import green_input, orange_print, yellow_print, blue_print, red_print


class FernetEncryptionMethod:
    def __init__(self, text):
        self._text = text

    def encryption(self):
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(self._text.encode('utf-8')).decode('utf-8')
        key = key.decode('utf-8')
        return key, cipher_text


class FernetDecryptionMethod:
    def __init__(self, text, key):
        self._text = text
        self._key = key

    def decryption(self):
        cipher_suite = Fernet(self._key.encode('ascii'))  # 使用用户输入的密钥创建Fernet对象
        plain_text = cipher_suite.decrypt(self._text.encode('utf-8')).decode('utf-8')
        return plain_text


if __name__ == '__main__':
    while True:
        try:
            text = green_input("请输入要加密的内容(输入q退出): ")
            if text == 'q':
                orange_print("已退出")
                break
            FEM = FernetEncryptionMethod(text)
            key, cipher_text = FEM.encryption()
            yellow_print(f'密文: {cipher_text}')
            blue_print(f'密钥: {key}\n')

            cipher_text = green_input("请输入要解密的内容(输入q退出): ")
            if cipher_text == 'q':
                orange_print("已退出")
                break
            key = green_input("请输入密钥(输入q退出): ")
            if key == 'q':
                orange_print("已退出")
                break
            FDM = FernetDecryptionMethod(cipher_text, key)
            plain_text = FDM.decryption()
            yellow_print(f'明文: {plain_text}\n')
        except ValueError:
            red_print("错误: 无效的密钥, 请输入32个URL安全的base64编码字节\n")
        except InvalidToken:
            red_print("错误: 解密失败, 密钥或密文无效\n")
        except KeyboardInterrupt:
            red_print("\n程序已强制中断")
            break
