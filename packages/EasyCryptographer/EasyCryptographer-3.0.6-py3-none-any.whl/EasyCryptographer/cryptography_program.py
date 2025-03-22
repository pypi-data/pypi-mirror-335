import binascii
import os
import sys
import tkinter as tk

from PIL import ImageTk, Image
from TkinterLite.easy_auto_window import EasyAutoWindow
from TkinterLite.easy_auto_window_size import auto_size
from TkinterLite.easy_button import EasyButton
from TkinterLite.easy_check_button import EasyCheckButton
from TkinterLite.easy_drop_list import EasyDropList
from TkinterLite.easy_fade_animation import fade_out, fade_in
from TkinterLite.easy_frame import EasyFrame
from TkinterLite.easy_label import EasyLabel
from TkinterLite.easy_mobile_animation import move_window_to
from TkinterLite.easy_multi_text import EasyMultiText
from TkinterLite.easy_popup_animation import animate_resize_window
from TkinterLite.easy_warning_windows import EasyWarningWindows
from cryptography.exceptions import InvalidTag
from cryptography.fernet import InvalidToken

from EasyCryptographer.convention.AEAD.AEAD_method import AEADEncryptionMethod, AEADDecryptionMethod
from EasyCryptographer.convention.AES.AES_method import AESEncryptionMethod, AESDecryptionMethod
from EasyCryptographer.convention.Blowfish.Blowfish_method import BlowfishEncryptionMethod, BlowfishDecryptionMethod
from EasyCryptographer.convention.CAST5.CAST5_method import CAST5EncryptionMethod, CAST5DecryptionMethod
from EasyCryptographer.convention.Camellia.Camellia_method import CamelliaEncryptionMethod, CamelliaDecryptionMethod
from EasyCryptographer.convention.Fernet.Fernet_method import FernetEncryptionMethod, FernetDecryptionMethod
from EasyCryptographer.convention.RC4.RC4_method import RC4EncryptionMethod, RC4DecryptionMethod
from EasyCryptographer.convention.RSA.RSA_method import RSAEncryptionMethod, RSADecryptionMethod


def check_and_create_file(filename, home_dir, write):
    home_dir = os.path.expanduser(home_dir)
    file_path = os.path.join(home_dir, filename)

    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(write)


check_and_create_file("algorithm_settings.txt", "~", "自动")
check_and_create_file("instructions_settings.txt", "~", "开")
check_and_create_file("unsaved_reminder_settings.txt", "~", "开")
check_and_create_file("error_prompt_settings.txt", "~", "开")
check_and_create_file("auto_save_settings.txt", "~", "开")
check_and_create_file("auto_save_settings2.txt", "~", "开")
check_and_create_file("enable_shortcut_keys.txt", "~", "开")


def resource_path(relative_path):
    home_dir = os.path.expanduser('~')
    file_path = os.path.join(home_dir, relative_path)
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, file_path)
    return file_path


cryptography_settings = resource_path('algorithm_settings.txt')
instructions_settings = resource_path('instructions_settings.txt')
unsaved_reminder_settings = resource_path('unsaved_reminder_settings.txt')
error_prompt_settings = resource_path('error_prompt_settings.txt')
auto_save_settings = resource_path('auto_save_settings.txt')
auto_save_settings2 = resource_path('auto_save_settings2.txt')
shortcut_keys_settings = resource_path('enable_shortcut_keys.txt')
logo = resource_path('logo.ico')


def quit_window():
    global settings_window, settings_num, instructions_num

    if settings_num == 1:
        on_settings_window_close()
    if instructions_num == 1:
        on_instructions_window_close()
    fade_out(window)


def on_settings_window_close():
    global settings_window, settings_num, unsaved_reminder_settings_value, error_prompt_settings_value, \
        auto_save_settings_value, shortcut_keys_settings_value, other_settings

    file_list = []
    obtain_list = other_settings.get_set()

    with open(unsaved_reminder_settings, 'r', encoding='utf-8') as file:
        unsaved_reminder_settings_value = file.read()
    if unsaved_reminder_settings_value == "开":
        file_list.append("退出设置未保存时提醒")

    with open(error_prompt_settings, 'r', encoding='utf-8') as file:
        error_prompt_settings_value = file.read()
    if error_prompt_settings_value == "开":
        file_list.append("加密解密出错时弹出错误提示")

    with open(auto_save_settings, 'r', encoding='utf-8') as file:
        auto_save_settings_value = file.read()
    if auto_save_settings_value == "开":
        file_list.append("重置设置后自动保存")

    with open(shortcut_keys_settings, 'r', encoding='utf-8') as file:
        shortcut_keys_settings_value = file.read()
    if shortcut_keys_settings_value == "开":
        file_list.append("启用快捷键")

    with open(auto_save_settings2, 'r', encoding='utf-8') as file:
        auto_save_settings2_value = file.read()
    if auto_save_settings2_value == "开":
        file_list.append("自动保存设置")

    if unsaved_reminder_settings_value == "开" and obtain_list != file_list:
        result = EasyWarningWindows(settings_window, "是/否", "是否保存更改？").show_warning()
        if result:
            save_settings()
    fade_out(settings_window)
    settings_num -= 1


def on_instructions_window_close():
    global instructions_window, instructions_num

    result = EasyWarningWindows(instructions_window, "是/否", "下次打开程序时是否需要自动打开此窗口？").show_warning()
    if result:
        with open(instructions_settings, 'w') as file:
            file.write("开")
    else:
        with open(instructions_settings, 'w') as file:
            file.write("关")
    fade_out(instructions_window)
    instructions_num -= 1


def replace(text_box, text):
    text_box.get_text().config(state="normal")
    text_box.get_text().delete("1.0", tk.END)
    text_box.get_text().insert(tk.END, text)
    text_box.get_text().config(state="disabled")


def get_data():
    global error_prompt_settings_value

    with open(error_prompt_settings, 'r', encoding='utf-8') as file:
        error_prompt_settings_value = file.read()

    try:
        decryption_text = decryption_text_need.get_content()
        key_and_algorithm = key_text_need.get_content()
        algorithm_choice = key_and_algorithm[0]
        key = key_and_algorithm[1:]
        return decryption_text, algorithm_choice, key
    except IndexError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n密文或密钥不正确").show_warning()


def AES_encryption():
    encryption_need = encryption_text_need.get_content()
    if encryption_need == '':
        window.bell()
        EasyWarningWindows(window, "警告", "错误\n\n请输入需要加密的文本").show_warning()
        return
    encrypt_obj = AESEncryptionMethod(encryption_need)
    cipher_text, key = encrypt_obj.encryption()
    key = f'2{key}'
    replace(key_text, key)
    replace(encryption_text_after, cipher_text)


def Fernet_encryption():
    encryption_need = encryption_text_need.get_content()
    if encryption_need == '':
        window.bell()
        EasyWarningWindows(window, "警告", "错误\n\n请输入需要加密的文本").show_warning()
        return
    CEM = FernetEncryptionMethod(encryption_need)
    key, cipher_text = CEM.encryption()
    key = f'3{key}'
    replace(key_text, key)
    replace(encryption_text_after, cipher_text)


def RSA_encryption():
    encryption_need = encryption_text_need.get_content()
    if encryption_need == '':
        window.bell()
        EasyWarningWindows(window, "警告", "错误\n\n请输入需要加密的文本").show_warning()
        return
    REM = RSAEncryptionMethod(encryption_need)
    cipher_text, key = REM.encryption()
    key = f'4{key}'
    replace(key_text, key)
    replace(encryption_text_after, cipher_text)


def AEAD_encryption():
    encryption_need = encryption_text_need.get_content()
    if encryption_need == '':
        window.bell()
        EasyWarningWindows(window, "警告", "错误\n\n请输入需要加密的文本").show_warning()
        return
    AEADEM = AEADEncryptionMethod(encryption_need)
    cipher_text, key = AEADEM.encryption()
    key = f'5{key}'
    replace(key_text, key)
    replace(encryption_text_after, cipher_text)


def Blowfish_encryption():
    encryption_need = encryption_text_need.get_content()
    if encryption_need == '':
        window.bell()
        EasyWarningWindows(window, "警告", "错误\n\n请输入需要加密的文本").show_warning()
        return
    BEM = BlowfishEncryptionMethod(encryption_need)
    cipher_text, key = BEM.encryption()
    key = f'6{key}'
    replace(key_text, key)
    replace(encryption_text_after, cipher_text)


def CAST5_encryption():
    encryption_need = encryption_text_need.get_content()
    if encryption_need == '':
        window.bell()
        EasyWarningWindows(window, "警告", "错误\n\n请输入需要加密的文本").show_warning()
        return
    CEM = CAST5EncryptionMethod(encryption_need)
    cipher_text, key = CEM.encryption()
    key = f'7{key}'
    replace(key_text, key)
    replace(encryption_text_after, cipher_text)


def RC4_encryption():
    encryption_need = encryption_text_need.get_content()
    if encryption_need == '':
        window.bell()
        EasyWarningWindows(window, "警告", "错误\n\n请输入需要加密的文本").show_warning()
        return
    REM = RC4EncryptionMethod(encryption_text_need.get_content())
    cipher_text, key = REM.encryption()
    key = f'8{key}'
    replace(key_text, key)
    replace(encryption_text_after, cipher_text)


def Camellia_encryption():
    encryption_need = encryption_text_need.get_content()
    if encryption_need == '':
        window.bell()
        EasyWarningWindows(window, "警告", "错误\n\n请输入需要加密的文本").show_warning()
        return
    CEM = CamelliaEncryptionMethod(encryption_need)
    cipher_text, key = CEM.encryption()
    key = f'9{key}'
    replace(key_text, key)
    replace(encryption_text_after, cipher_text)


def auto_encryption():
    encryption_need_length = len(encryption_text_need.get_content().encode('utf-8'))
    if encryption_need_length <= 16:
        AES_encryption()
    elif encryption_need_length <= 32:
        Camellia_encryption()
    elif encryption_need_length <= 64:
        Fernet_encryption()
    elif encryption_need_length <= 128:
        RSA_encryption()
    elif encryption_need_length <= 256:
        Blowfish_encryption()
    else:
        CAST5_encryption()


def AES_decryption(decryption_text, key):
    global error_prompt_settings_value

    with open(error_prompt_settings, 'r', encoding='utf-8') as fire:
        error_prompt_settings_value = fire.read()

    try:
        decrypt_obj = AESDecryptionMethod(decryption_text, key)
        plain_text = decrypt_obj.decryption()
        replace(decryption_text_after, plain_text)
    except TypeError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n无效的密钥, 请输入正确的Base64编码密钥").show_warning()
    except binascii.Error:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n密钥长度不正确, 请输入正确的Base64编码密钥").show_warning()
    except InvalidTag:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n解密失败, 密钥不正确").show_warning()
    except ValueError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n解密失败, 密文长度不正确").show_warning()
    except Exception as e:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows("警告", f"未知错误\n\n{str(e)}").show_warning()


def Fernet_decryption(decryption_text, key):
    global error_prompt_settings_value

    with open(error_prompt_settings, 'r', encoding='utf-8') as file:
        error_prompt_settings_value = file.read()

    try:
        CDM = FernetDecryptionMethod(decryption_text, key)
        plain_text = CDM.decryption()
        replace(decryption_text_after, plain_text)
    except ValueError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n无效的密钥, 请输入32个URL安全的base64编码字节").show_warning()
    except InvalidToken:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n解密失败, 密钥或密文无效").show_warning()


def RSA_decryption(decryption_text, key):
    global error_prompt_settings_value

    with open(error_prompt_settings, 'r', encoding='utf-8') as fire:
        error_prompt_settings_value = fire.read()

    try:
        RDM = RSADecryptionMethod(decryption_text, key)
        plain_text = RDM.decryption()
        replace(decryption_text_after, plain_text)
    except UnicodeDecodeError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告",
                               "错误\n\n解密后的数据无法使用UTF-8编码解码, 请检查输入的密钥是否正确").show_warning()
    except ValueError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n输入的密钥或密文不正确").show_warning()
    except IndexError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n解密失败, 密钥或密文错误").show_warning()


def AEAD_decryption(decryption_text, key):
    global error_prompt_settings_value

    with open(error_prompt_settings, 'r', encoding='utf-8') as file:
        error_prompt_settings_value = file.read()

    try:
        AEADDM = AEADDecryptionMethod(decryption_text, key)
        plain_text = AEADDM.decryption()
        replace(decryption_text_after, plain_text)
    except ValueError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n解密失败, 无效的密文或密钥").show_warning()
    except IndexError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n解密失败, 密钥或密文错误").show_warning()


def Blowfish_decryption(decryption_text, key):
    global error_prompt_settings_value

    with open(error_prompt_settings, 'r', encoding='utf-8') as file:
        error_prompt_settings_value = file.read()

    try:
        BDM = BlowfishDecryptionMethod(decryption_text, key)
        plain_text = BDM.decryption()
        replace(decryption_text_after, plain_text)
    except ValueError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n无效的密文或密钥").show_warning()
    except Exception:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n解密失败").show_warning()


def CAST5_decryption(decryption_text, key):
    global error_prompt_settings_value

    with open(error_prompt_settings, 'r', encoding='utf-8') as file:
        error_prompt_settings_value = file.read()

    try:
        CADM = CAST5DecryptionMethod(decryption_text, key)
        plain_text = CADM.decryption()
        replace(decryption_text_after, plain_text)
    except ValueError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n无效的密文或密钥").show_warning()
    except Exception:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n解密失败").show_warning()


def RC4_decryption(decryption_text, key):
    global error_prompt_settings_value

    with open(error_prompt_settings, 'r', encoding='utf-8') as file:
        error_prompt_settings_value = file.read()

    try:
        RDM = RC4DecryptionMethod(decryption_text, key)
        plain_text = RDM.decryption()
        replace(decryption_text_after, plain_text)
    except UnicodeDecodeError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n无效的密文或密钥").show_warning()
    except ValueError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n无效的密文或密钥").show_warning()
    except Exception:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "错误\n\n解密失败").show_warning()


def Camellia_decryption(decryption_text, key):
    global error_prompt_settings_value

    with open(error_prompt_settings, 'r', encoding='utf-8') as file:
        error_prompt_settings_value = file.read()

    try:
        CDM = CamelliaDecryptionMethod(decryption_text, key)
        plain_text = CDM.decryption()
        replace(decryption_text_after, plain_text)
    except UnicodeDecodeError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告",
                               "错误\n\n解密后的数据无法使用UTF-8编码解码, 请检查输入的密钥是否正确").show_warning()
    except ValueError:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告",
                               "错误\n\n无效的密文或密钥, 请确保输入正确的十六进制字符串").show_warning()
    except Exception:
        window.bell()
        if error_prompt_settings_value == "开":
            EasyWarningWindows(window, "警告", "解密失败\n")


def encryption():
    global algorithm_settings

    result = True
    if len(encryption_text_need.get_content().encode('utf-8')) >= 10000:
        result = EasyWarningWindows(window, "是/否",
                                    "您需要加密的字数已经超过了10000个字符, 继续加密很可能导致程序卡死或无法退出, 是否继续加密？").show_warning()
    if result:
        with open(cryptography_settings, 'r', encoding='utf-8') as file:
            algorithm_settings = file.read()
        if algorithm_settings == '自动':
            algorithm_settings = 1
        elif algorithm_settings == 'AEAD':
            algorithm_settings = 2
        elif algorithm_settings == 'AES':
            algorithm_settings = 3
        elif algorithm_settings == 'Camellia':
            algorithm_settings = 4
        elif algorithm_settings == 'Fernet':
            algorithm_settings = 5
        elif algorithm_settings == 'RSA':
            algorithm_settings = 6
        elif algorithm_settings == 'Blowfish':
            algorithm_settings = 7
        elif algorithm_settings == 'CAST5':
            algorithm_settings = 8
        elif algorithm_settings == 'RC4':
            algorithm_settings = 9
        if algorithm_settings == 1:
            auto_encryption()
        elif algorithm_settings == 2:
            AEAD_encryption()
        elif algorithm_settings == 3:
            AES_encryption()
        elif algorithm_settings == 4:
            Camellia_encryption()
        elif algorithm_settings == 5:
            Fernet_encryption()
        elif algorithm_settings == 6:
            RSA_encryption()
        elif algorithm_settings == 7:
            Blowfish_encryption()
        elif algorithm_settings == 8:
            CAST5_encryption()
        elif algorithm_settings == 9:
            RC4_encryption()


def decryption():
    global error_prompt_settings_value

    with open(error_prompt_settings, 'r', encoding='utf-8') as fire:
        error_prompt_settings_value = fire.read()

    try:
        decryption_text, algorithm_choice, key = get_data()

        result = True
        if len(decryption_text) >= 10000:
            result = EasyWarningWindows(window, "是/否",
                                        "您需要解密的字数已经超过了10000个字符, 继续解密很可能导致程序卡死或无法退出, 是否继续解密？").show_warning()
        if result:
            if decryption_text == '':
                window.bell()
                if error_prompt_settings_value == "开":
                    EasyWarningWindows(window, "警告", "错误\n\n密文为空").show_warning()

            if algorithm_choice == '2':
                AES_decryption(decryption_text, key)
            elif algorithm_choice == '3':
                Fernet_decryption(decryption_text, key)
            elif algorithm_choice == '4':
                RSA_decryption(decryption_text, key)
            elif algorithm_choice == '5':
                AEAD_decryption(decryption_text, key)
            elif algorithm_choice == '6':
                Blowfish_decryption(decryption_text, key)
            elif algorithm_choice == '7':
                CAST5_decryption(decryption_text, key)
            elif algorithm_choice == '8':
                RC4_decryption(decryption_text, key)
            elif algorithm_choice == '9':
                Camellia_decryption(decryption_text, key)
            else:
                window.bell()
                if error_prompt_settings_value == "开":
                    EasyWarningWindows(window, "警告", "错误\n\n密钥或密文错误").show_warning()
    except TypeError:
        return


def save_settings(*args):
    global algorithm, other_settings, instructions_num

    other_settings_set = other_settings.get_set()

    with open(cryptography_settings, 'w', encoding='utf-8') as file_local:
        file_local.write(algorithm.get_combo_value())

    with open(unsaved_reminder_settings, 'w', encoding='utf-8') as file:
        if "退出设置未保存时提醒" in other_settings_set:
            file.write("开")
        else:
            file.write("关")

    with open(error_prompt_settings, 'w', encoding='utf-8') as file:
        if "加密解密出错时弹出错误提示" in other_settings_set:
            file.write("开")
        else:
            file.write("关")

    with open(auto_save_settings, 'w', encoding='utf-8') as file:
        if "重置设置后自动保存" in other_settings_set:
            file.write("开")
        else:
            file.write("关")

    with open(shortcut_keys_settings, 'w', encoding='utf-8') as file:
        if "启用快捷键" in other_settings_set:
            file.write("开")
            window.bind('<Command-comma>', lambda event: settings())
            window.bind('<F1>', lambda event: instructions())
            window.bind('<q>', lambda event: quit_window())
            window.bind('<Q>', lambda event: quit_window())
            settings_window.bind('<Command-comma>', lambda event: settings())
            settings_window.bind('<F1>', lambda event: instructions())
            settings_window.bind('<q>', lambda event: quit_window())
            settings_window.bind('<Q>', lambda event: quit_window())
            if instructions_num == 1:
                instructions_window.bind('<Command-comma>', lambda event: settings())
                instructions_window.bind('<F1>', lambda event: instructions())
                instructions_window.bind('<q>', lambda event: quit_window())
                instructions_window.bind('<Q>', lambda event: quit_window())
        else:
            file.write("关")
            window.unbind('<Command-comma>')
            window.unbind('<F1>')
            window.unbind('<q>')
            window.unbind('<Q>')
            settings_window.unbind('<Command-comma>')
            settings_window.unbind('<F1>')
            settings_window.unbind('<q>')
            settings_window.unbind('<Q>')
            if instructions_num == 1:
                instructions_window.unbind('<Command-comma>')
                instructions_window.unbind('<F1>')
                instructions_window.unbind('<q>')
                instructions_window.unbind('<Q>')

    with open(auto_save_settings2, 'w', encoding='utf-8') as file:
        if "自动保存设置" in other_settings_set:
            file.write("开")
        else:
            file.write("关")


def reset_settings():
    global algorithm, other_settings, auto_save_settings_value

    with open(auto_save_settings, 'r', encoding='utf-8') as file:
        auto_save_settings_value = file.read()

    result = EasyWarningWindows(settings_window, "是/否", "您确定要重置设置吗？").show_warning()
    if result:
        algorithm.set_combo_value('自动')
        other_settings.set(["退出设置未保存时提醒", "加密解密出错时弹出错误提示", "重置设置后自动保存", "启用快捷键",
                            "自动保存设置"])
        if auto_save_settings_value == "开":
            save_settings()


def center_window(root):
    width = root.winfo_width()
    height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2 - 20

    root.lift()
    root.focus_set()
    move_window_to(root, x, y, 150, 0.2, "ordinary")


def about_keys():
    global settings_window

    EasyWarningWindows(settings_window, "信息", "按下q键退出\n按下F1显示使用说明").show_warning()


def settings():
    global settings_window, settings_num, algorithm, algorithm_settings, other_settings, \
        unsaved_reminder_settings_value, error_prompt_settings_value, auto_save_settings_value, \
        shortcut_keys_settings_value, auto_save_settings_value2, command, window

    if settings_num != 1:
        settings_num += 1

        command = None

        with open(cryptography_settings, 'r', encoding='utf-8') as file:
            algorithm_settings = file.read()
        if algorithm_settings == '自动':
            algorithm_settings = 1
        elif algorithm_settings == 'AEAD':
            algorithm_settings = 2
        elif algorithm_settings == 'AES':
            algorithm_settings = 3
        elif algorithm_settings == 'Camellia':
            algorithm_settings = 4
        elif algorithm_settings == 'Fernet':
            algorithm_settings = 5
        elif algorithm_settings == 'RSA':
            algorithm_settings = 6
        elif algorithm_settings == 'Blowfish':
            algorithm_settings = 7
        elif algorithm_settings == 'CAST5':
            algorithm_settings = 8
        elif algorithm_settings == 'RC4':
            algorithm_settings = 9

        with open(unsaved_reminder_settings, 'r', encoding='utf-8') as file:
            unsaved_reminder_settings_value = file.read()

        with open(error_prompt_settings, 'r', encoding='utf-8') as file:
            error_prompt_settings_value = file.read()

        with open(auto_save_settings, 'r', encoding='utf-8') as file:
            auto_save_settings_value = file.read()

        with open(auto_save_settings2, 'r', encoding='utf-8') as file:
            auto_save_settings_value2 = file.read()

        with open(shortcut_keys_settings, 'r', encoding='utf-8') as file:
            shortcut_keys_settings_value = file.read()

        other_settings_set = []
        if unsaved_reminder_settings_value == "开":
            other_settings_set.append("退出设置未保存时提醒")
        if error_prompt_settings_value == "开":
            other_settings_set.append("加密解密出错时弹出错误提示")
        if auto_save_settings_value == "开":
            other_settings_set.append("重置设置后自动保存")
        if shortcut_keys_settings_value == "开":
            other_settings_set.append("启用快捷键")
        if auto_save_settings_value2 == "开":
            other_settings_set.append("自动保存设置")
            command = save_settings

        settings_window = tk.Toplevel(window)

        EasyAutoWindow(settings_window, window_title="设置", window_width_value=280, window_height_value=140,
                       adjust_x=False, adjust_y=False)

        fade_in(settings_window, ms=2)
        animate_resize_window(settings_window, 780, 340, 250, "ordinary", False)

        f1 = EasyFrame(settings_window, fill=tk.BOTH, side=tk.TOP, expand=tk.YES, is_debug=False).get()
        f11 = EasyFrame(f1, fill=tk.BOTH, side=tk.TOP, expand=tk.YES, is_debug=False).get()
        f12 = EasyFrame(f1, fill=tk.BOTH, side=tk.TOP, expand=tk.YES, is_debug=False).get()
        f13 = EasyFrame(f1, fill=tk.BOTH, side=tk.TOP, expand=tk.YES, is_debug=False).get()
        f14 = EasyFrame(f1, fill=tk.BOTH, side=tk.TOP, expand=tk.YES, is_debug=False).get()
        f2 = EasyFrame(settings_window, fill=tk.BOTH, side=tk.TOP, expand=tk.YES, is_debug=False).get()

        EasyLabel(f11, text="加密算法:", side=tk.LEFT)
        algorithm = EasyDropList(f11, options=['自动', 'AEAD', 'AES', 'Camellia', 'Fernet', 'RSA', 'Blowfish', 'CAST5',
                                               'RC4'], default=algorithm_settings, side=tk.LEFT, cmd=save_settings)
        EasyLabel(f11, text="*越靠上的算法越安全", side=tk.LEFT, font_size=12, text_color="gray")

        EasyLabel(f12, text="由于程序会根据密钥自动检测加密的算法来匹配解密的算法, 所以无需设置解密的算法",
                  side=tk.LEFT, font_size=12)

        other_settings = EasyCheckButton(f13, text=["退出设置未保存时提醒", "加密解密出错时弹出错误提示",
                                                    "重置设置后自动保存", "启用快捷键", "自动保存设置"],
                                         set_text_list=other_settings_set, master_win=window, expand=True, fill=tk.Y,
                                         cmd=command)

        EasyButton(f14, text="关于快捷键", cmd=about_keys, side=tk.LEFT, width=10, height=1,
                   font_size=12)

        EasyButton(f2, text="保存", expand=tk.YES, height=2, cmd=save_settings, side=tk.LEFT,
                   fill=tk.X)

        EasyButton(f2, text="退出", expand=tk.YES, height=2, cmd=on_settings_window_close, side=tk.LEFT,
                   fill=tk.X)

        EasyButton(f2, text="重置", expand=tk.YES, height=2, cmd=reset_settings, side=tk.LEFT,
                   fill=tk.X)

        settings_window.protocol("WM_DELETE_WINDOW", on_settings_window_close)

        with open(shortcut_keys_settings, 'r', encoding='utf-8') as file:
            shortcut_keys_settings_value = file.read()

        if shortcut_keys_settings_value == "开":
            settings_window.bind('<Command-comma>', lambda event: settings())
            settings_window.bind('<F1>', lambda event: instructions())
            settings_window.bind('<q>', lambda event: quit_window())
            settings_window.bind('<Q>', lambda event: quit_window())

    else:
        center_window(settings_window)


def instructions():
    global instructions_num, instructions_window, shortcut_keys_settings_value

    if instructions_num != 1:
        instructions_num += 1
        instructions_window = tk.Toplevel()
        instructions_text = ("加密方法: 将需要加密的文本输入到指定的文本框内, 然后点击加密按钮, 加密后的文本和密钥就会显示在指定的文本"
                             "框内。您可以在设置窗口里面调整加密的算法, 默认为自动\n\n\n解密方法: 将密文和密钥输入到指定的文本框内, 然"
                             "后点击解密按钮, 解密后的文本就会显示在指定的文本框内, 程序会根据密钥自动匹配解密算法。(注: 如果解密出错,"
                             " 程序会弹出错误提示, 如果没有看见弹窗, 可能是被设置或者其他窗口挡住了)\n\n\n设置说明: 在设置中, 你可以"
                             "设置加密的算法和其他的功能。(注: 由于程序会根据密钥自动检测加密的算法来匹配解密的算法, 所以无需设置解密的"
                             "算法)如果您想要恢复默认设置, 请点击重置按钮。如果您想要保存您的更改, 请点击保存按钮。如果您想要退出设置, "
                             "请点击退出按钮。\n\n\n关于设置: 点击加密解密窗口下方的设置按钮, 程序就会弹出设置窗口。在设置里, 您可以选"
                             "择加密解密的算法。\n\n\n注意事项: 请不要全屏显示窗口, 全屏模式下, 显示会有一些问题。\n\n\n快捷键: 您可"
                             "以通过按q键来关闭程序, 您也可以通过按command键加逗号来打开设置窗口, 您还可以按F1键来打开使用方法窗口。")

        EasyAutoWindow(instructions_window, window_title="使用方法", window_width_value=230, window_height_value=170,
                       minimum_value_x=230, minimum_value_y=170)

        fade_in(instructions_window, ms=2)
        animate_resize_window(instructions_window, 600, 400, 200, "ordinary", False)

        instructions_box = EasyMultiText(instructions_window, expand=tk.YES, fill=tk.BOTH)
        replace(instructions_box, instructions_text)

        instructions_window.protocol("WM_DELETE_WINDOW", on_instructions_window_close)

        with open(shortcut_keys_settings, 'r', encoding='utf-8') as file:
            shortcut_keys_settings_value = file.read()

        if shortcut_keys_settings_value == "开":
            instructions_window.bind('<F1>', lambda event: instructions())
            instructions_window.bind('<Command-comma>', lambda event: settings())
            instructions_window.bind('<q>', lambda event: quit_window())
            instructions_window.bind('<Q>', lambda event: quit_window())
    else:
        center_window(instructions_window)


settings_window = None
algorithm = None
algorithm_settings = None
instructions_window = None
other_settings = None
unsaved_reminder_settings_value = None
error_prompt_settings_value = None
auto_save_settings_value = None
auto_save_settings_value2 = None
shortcut_keys_settings_value = None
command = None
instructions_num = 0
settings_num = 0

window = tk.Tk()

icon_image = ImageTk.PhotoImage(Image.open(logo))
window.iconphoto(True, icon_image)

window_width_value, window_height_value, _, _ = auto_size(window)

EasyAutoWindow(window, window_title="cryptography", minimum_value_x=636, minimum_value_y=834, window_width_value=636,
               window_height_value=834)

fade_in(window, ms=1)
animate_resize_window(window, window_width_value, window_height_value, 120, "ordinary", False)

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

EasyButton(window, text="退出", fill=tk.BOTH, expand=tk.YES, side=tk.LEFT, height=2, cmd=quit_window)

EasyButton(window, text="设置", fill=tk.BOTH, expand=tk.YES, side=tk.LEFT, height=2, cmd=settings)

EasyButton(window, text="使用方法", fill=tk.BOTH, expand=tk.YES, side=tk.LEFT, height=2, cmd=instructions)

with open(instructions_settings, 'r', encoding='utf-8') as file:
    auto_open_instructions_window = file.read()
if auto_open_instructions_window == "开":
    instructions()

window.protocol("WM_DELETE_WINDOW", quit_window)

with open(shortcut_keys_settings, 'r', encoding='utf-8') as file:
    shortcut_keys_settings_value = file.read()

if shortcut_keys_settings_value == "开":
    window.bind('<Command-comma>', lambda event: settings())
    window.bind('<F1>', lambda event: instructions())
    window.bind('<q>', lambda event: quit_window())
    window.bind('<Q>', lambda event: quit_window())

window.mainloop()
