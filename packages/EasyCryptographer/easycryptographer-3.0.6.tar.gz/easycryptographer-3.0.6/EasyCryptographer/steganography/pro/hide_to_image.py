from PIL import Image
from publicmodel.common import animation_progress_bar, auto_line_wrap

from EasyCryptographer import SecurityLevelError, ImageError


class Encryptor:
    def __init__(self, image_path, text, security_level=3):
        self.image_path = image_path
        self.text = text
        self.security_level = security_level

        if security_level not in [1, 2, 3]:
            raise SecurityLevelError("Invalid security level. Choose from 1, 2, or 3.")

    def text_to_binary(self):
        binary = ''.join(format(byte, '08b') for byte in self.text.encode('utf-8'))
        return binary

    def binary_to_rgb(self, binary):
        rgb_values = []
        for i in range(0, len(binary), 8 * self.security_level):
            r = int(binary[i:i + 8], 2) if i + 8 <= len(binary) else 0
            g = int(binary[i + 8:i + 16], 2) if i + 16 <= len(binary) else 0
            b = int(binary[i + 16:i + 24], 2) if i + 24 <= len(binary) else 0
            rgb_values.append((r, g, b))
        return rgb_values

    def create_image(self):
        binary = self.text_to_binary()
        text_length = len(self.text.encode('utf-8'))
        length_binary = format(text_length, '032b')  # 32-bit binary length
        binary = length_binary + binary

        rgb_values = self.binary_to_rgb(binary)

        image = Image.open(self.image_path)
        pixels = list(image.getdata())

        if len(rgb_values) > len(pixels):
            raise ImageError("The image is too small to hold the message.")

        # Embed security level in the top-left pixel
        security_pixel = (self.security_level, self.security_level, self.security_level)
        pixels[0] = security_pixel

        for i in range(len(rgb_values)):
            r, g, b = pixels[i + 1]  # Start from the second pixel
            if self.security_level == 1:
                r = rgb_values[i][0]
            elif self.security_level == 2:
                r = rgb_values[i][0]
                g = rgb_values[i][1]
            elif self.security_level == 3:
                r = rgb_values[i][0]
                g = rgb_values[i][1]
                b = rgb_values[i][2]
            pixels[i + 1] = (r, g, b)

        image.putdata(pixels)
        return image

    def save_image(self, filename):
        image = self.create_image()
        image.save(filename)


class Decryptor:
    def __init__(self, image_path):
        self.image_path = image_path

    def extract_text(self):
        image = Image.open(self.image_path)
        pixels = list(image.getdata())

        # Read security level from the top-left pixel
        security_pixel = pixels[0]
        security_level = min(security_pixel[0], 3)
        binary = ''
        for pixel in pixels[1:]:  # Start from the second pixel
            r, g, b = pixel
            if security_level == 1:
                binary += format(r, '08b')
            elif security_level == 2:
                binary += format(r, '08b') + format(g, '08b')
            elif security_level == 3:
                binary += format(r, '08b') + format(g, '08b') + format(b, '08b')

        length_binary = binary[:32]
        text_length = int(length_binary, 2)
        text_binary = binary[32:32 + text_length * 8]

        text_bytes = bytearray()
        for i in range(0, len(text_binary), 8):
            byte = text_binary[i:i + 8]
            text_bytes.append(int(byte, 2))

        text = text_bytes.decode('utf-8')
        return text


if __name__ == '__main__':
    text = (
        "Steganography is a technique used to hide information within other non-secret data. In encryption, text"
        " is converted into binary and embedded into an image's pixel values. The image size is adjusted to"
        " accommodate the data. For decryption, the binary data is extracted from the image and converted back to"
        " text. This method ensures that the hidden message is not easily detectable, providing an additional layer"
        " of security."
    )

    image_path = '../../images/hide_to_image_pro_input.png'
    security_level = 3

    encryptor = Encryptor(image_path, text, security_level)
    animation_progress_bar(
        "Encrypting...",
        None,
        0.25,
        encryptor.save_image,
        "process",
        '../../images/hide_to_image_pro_output.png',
    )
    print("Encryption is complete.")

    decryptor = Decryptor('../../images/hide_to_image_pro_output.png')
    extracted_text = animation_progress_bar(
        "Decrypting...",
        None,
        0.25,
        decryptor.extract_text,
        "process",
    )

    new_extracted_text = auto_line_wrap(extracted_text, 100, True)

    print("Decryption is completed.\n")
    print("Decrypted text:")
    print(new_extracted_text)
