import math

from PIL import Image


class Encryptor:
    def __init__(self, text, image_size=None):
        self.text = text
        self.image_size = image_size

    def text_to_binary(self):
        binary = ''.join(format(byte, '08b') for byte in self.text.encode('utf-8'))
        return binary

    def binary_to_rgb(self, binary):
        rgb_values = []
        for i in range(0, len(binary), 24):
            r = int(binary[i:i + 8], 2) if i + 8 <= len(binary) else 0
            g = int(binary[i + 8:i + 16], 2) if i + 16 <= len(binary) else 0
            b = int(binary[i + 16:i + 24], 2) if i + 24 <= len(binary) else 0
            rgb_values.append((r, g, b))
        return rgb_values

    def calculate_image_size(self, num_pixels):
        side_length = math.ceil(math.sqrt(num_pixels))
        return (side_length, side_length)

    def create_image(self):
        binary = self.text_to_binary()
        text_length = len(self.text.encode('utf-8'))
        length_binary = format(text_length, '032b')  # 32-bit binary length
        binary = length_binary + binary  # Prepend length information
        rgb_values = self.binary_to_rgb(binary)

        if self.image_size is None:
            self.image_size = self.calculate_image_size(len(rgb_values))

        image = Image.new('RGB', self.image_size)
        image.putdata(rgb_values)
        return image

    def save_image(self, filename):
        image = self.create_image()
        image.save(filename)


class Decryptor:
    def __init__(self, image_path):
        self.image_path = image_path

    def rgb_to_binary(self, rgb_values):
        binary = ''.join(format(r, '08b') + format(g, '08b') + format(b, '08b') for r, g, b in rgb_values)
        return binary

    def binary_to_text(self, binary, text_length):
        byte_data = bytes(int(binary[i:i + 8], 2) for i in range(0, text_length * 8, 8))
        text = byte_data.decode('utf-8')
        return text

    def extract_text(self):
        image = Image.open(self.image_path)
        rgb_values = list(image.getdata())
        binary = self.rgb_to_binary(rgb_values)
        length_binary = binary[:32]  # First 32 bits for length
        text_length = int(length_binary, 2)
        text_binary = binary[32:32 + text_length * 8]
        text = self.binary_to_text(text_binary, text_length)
        return text


if __name__ == '__main__':
    text = (
        "Steganography is a technique used to hide information within other non-secret data. In encryption, text"
        " is converted into binary and embedded into an image's pixel values. The image size is adjusted to"
        " accommodate the data. For decryption, the binary data is extracted from the image and converted back to"
        " text. This method ensures that the hidden message is not easily detectable, providing an additional layer"
        " of security."
    )

    image_size = None
    encryptor = Encryptor(text, image_size)
    encryptor.save_image('../../images/hide_to_image_lite.png')

    decryptor = Decryptor('../../images/hide_to_image_lite.png')
    extracted_text = decryptor.extract_text()
    print(extracted_text)
