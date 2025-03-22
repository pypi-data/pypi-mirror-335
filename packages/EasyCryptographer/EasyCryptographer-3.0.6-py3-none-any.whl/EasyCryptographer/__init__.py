from .convention.AEAD import AEAD_method
from .convention.AES import AES_method
from .convention.Blowfish import Blowfish_method
from .convention.CAST5 import CAST5_method
from .convention.Fernet import Fernet_method
from .convention.RC4 import RC4_method
from .convention.RSA import RSA_method
from .steganography import lite
from .steganography import pro

__version__ = "3.0.6"
__all__ = [
    'AEAD_method',
    'AES_method',
    'Blowfish_method',
    'CAST5_method',
    'string_to_binary',
    'Fernet_method',
    'RC4_method',
    'RSA_method',
    'lite',
    'pro',
    'binary_to_string',
    'segment_binary',
    'SecurityLevelError',
    'ImageError',
    'ParameterError',
    'UnknownError',
]


def string_to_binary(s):
    # 将字符串转换为二进制表示，使用 UTF-8 编码
    return ''.join(format(ord(char), '016b') for char in s)


def binary_to_string(b):
    # 将二进制表示转换回字符串
    chars = [chr(int(b[i:i + 16], 2)) for i in range(0, len(b), 16)]
    return ''.join(chars)


def segment_binary(b):
    original_str = binary_to_string(b)

    # 计算每个字符的平均二进制长度
    segment_length = len(b) // len(original_str)

    # 分段
    segments = [b[i:i + segment_length] for i in range(0, len(b), segment_length)]
    return segments


class SecurityLevelError(Exception):
    """Throw an exception when the security value is incorrect."""
    pass


class ImageError(Exception):
    """Throw an exception when the image is incorrect."""
    pass


class ParameterError(Exception):
    """Throw an exception when the parameter is incorrect."""
    pass


class UnknownError(Exception):
    """Throw an exception when the unknown error occurs."""
    pass


if __name__ == "__main__":
    original_string = "Hello EasyCryptographer"

    binary_representation = string_to_binary(original_string)
    print(f"Binary representation: {binary_representation}")

    segments = segment_binary(binary_representation)
    print(f"Segments: {segments}")

    combined_binary_str = ''.join(segments)
    print(f"Combined binary string: {combined_binary_str}")

    reconstructed_string = binary_to_string(combined_binary_str)
    print(f"Reconstructed string: {reconstructed_string}")
