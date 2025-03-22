import binascii
import tkinter as tk

from LeleEasyTkinter.easy_auto_window import EasyAutoWindow
from LeleEasyTkinter.easy_button import EasyButton
from LeleEasyTkinter.easy_frame import EasyFrame
from LeleEasyTkinter.easy_label import EasyLabel
from LeleEasyTkinter.easy_multi_text import EasyMultiText
from LeleEasyTkinter.easy_warning_windows import EasyWarningWindows
from cryptographer.AES.AES_method import AESEncryptionMethod, AESDecryptionMethod
from cryptography.exceptions import InvalidTag


def quit_window():
    window.destroy()


def set_txt_obj_text_value(text_obj, text_str: str):
    text_obj.get_text().config(state="normal")
    text_obj.get_text().delete("1.0", tk.END)
    text_obj.get_text().insert(tk.END, text_str)
    text_obj.get_text().config(state="disabled")


def encryption():
    encrypt_obj = AESEncryptionMethod(encryption_text_need.get_content())
    cipher_text, key = encrypt_obj.encryption()
    set_txt_obj_text_value(key_text, key)
    set_txt_obj_text_value(encryption_text_after, cipher_text)


def decryption():
    try:
        cipher_text = decryption_text_need.get_content()
        key = key_text_need.get_content()
        decrypt_obj = AESDecryptionMethod(cipher_text, key)
        plain_text = decrypt_obj.decryption()
        set_txt_obj_text_value(decryption_text_after, plain_text)
    except TypeError:
        EasyWarningWindows(window, "警告", "错误\n\n无效的密钥, 请输入正确的Base64编码密钥").show_warning()
    except binascii.Error:
        EasyWarningWindows(window, "警告", "错误\n\n密钥长度不正确, 请输入正确的Base64编码密钥").show_warning()
    except InvalidTag:
        EasyWarningWindows(window, "警告", "错误\n\n解密失败, 密钥不正确").show_warning()
    except ValueError:
        EasyWarningWindows(window, "警告", "错误\n\n解密失败, 密文长度不正确").show_warning()
    except Exception as e:
        EasyWarningWindows(window, "警告", f"未知错误\n\n{str(e)}").show_warning()


window = tk.Tk()
EasyAutoWindow(window, window_title="AESMethod", minimum_value_x=1312, minimum_value_y=876,
               window_width_value=1400, window_height_value=890)

f1 = EasyFrame(window, fill=tk.BOTH, side=tk.TOP, expand=tk.YES).get()
f11 = EasyFrame(f1, fill=tk.BOTH, side=tk.TOP, expand=tk.YES).get()
f12 = EasyFrame(f1, fill=tk.BOTH, side=tk.TOP, expand=tk.YES).get()
f13 = EasyFrame(f1, fill=tk.BOTH, side=tk.TOP, expand=tk.YES).get()
f14 = EasyFrame(f1, fill=tk.BOTH, side=tk.RIGHT, expand=tk.YES).get()

f2 = EasyFrame(window, fill=tk.BOTH, side=tk.TOP, expand=tk.YES).get()
f21 = EasyFrame(f2, fill=tk.BOTH, side=tk.TOP, expand=tk.YES).get()
f22 = EasyFrame(f2, fill=tk.BOTH, side=tk.TOP, expand=tk.YES).get()
f23 = EasyFrame(f2, fill=tk.BOTH, side=tk.TOP, expand=tk.YES).get()
f24 = EasyFrame(f2, fill=tk.BOTH, side=tk.RIGHT, expand=tk.YES).get()

EasyLabel(f11, text="要加密的文本:", side=tk.LEFT)
encryption_text_need = EasyMultiText(f11, fill=tk.BOTH, side=tk.RIGHT, expand=tk.YES)

EasyLabel(f12, text="加密时的密钥:", side=tk.LEFT)
key_text = EasyMultiText(f12, fill=tk.BOTH, side=tk.RIGHT, expand=tk.YES)
key_text.get_text().config(state="disabled")

EasyLabel(f13, text="加密后的文本:", side=tk.LEFT)
encryption_text_after = EasyMultiText(f13, fill=tk.BOTH, side=tk.RIGHT, expand=tk.YES)
encryption_text_after.get_text().config(state="disabled")

EasyButton(f14, text="加密", fill=tk.BOTH, side=tk.TOP, expand=tk.YES, height=2, cmd=encryption)

EasyLabel(f21, text="要解密的文本:", side=tk.LEFT)
decryption_text_need = EasyMultiText(f21, fill=tk.BOTH, side=tk.RIGHT, expand=tk.YES)

EasyLabel(f22, text="解密时的密钥:", side=tk.LEFT)
key_text_need = EasyMultiText(f22, fill=tk.BOTH, side=tk.RIGHT, expand=tk.YES)

EasyLabel(f23, text="解密后的文本:", side=tk.LEFT)
decryption_text_after = EasyMultiText(f23, fill=tk.BOTH, side=tk.RIGHT, expand=tk.YES)
decryption_text_after.get_text().config(state="disabled")

EasyButton(f24, text="解密", fill=tk.BOTH, side=tk.TOP, expand=tk.YES, height=2, cmd=decryption)

EasyButton(window, text="退出", fill=tk.BOTH, side=tk.TOP, expand=tk.NO, height=2, cmd=quit_window)

window.mainloop()
