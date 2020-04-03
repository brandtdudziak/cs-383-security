import numpy as np
import imageio
from bitarray import bitarray
from bitarray.util import ba2int, int2ba
import re

def get_header(image, header_start, header_length, bits):
    img = imageio.imread(image)
    height, width, _ = img.shape

    chars = []
    count = 0
    for r in range(height):
        for c in range(width):
            if count < header_start + header_length:
                previous_length = len(chars)
                chars.extend(list(str(int2ba((img[r,c,0] & bits).item())).split('\'')[1]))
                chars.extend(list(str(int2ba((img[r,c,1] & bits).item())).split('\'')[1]))
                chars.extend(list(str(int2ba((img[r,c,2] & bits).item())).split('\'')[1]))
                count += len(chars) - previous_length
    output = "".join(chars)[header_start:header_start + header_length]
    return ba2int(bitarray(output))

def text_with_header(image, bits):
    img = imageio.imread(image)
    height, width, _ = img.shape
    print("Height:", height, "Width:", width)

    length = get_header(image, 0, 32, bits)
    print(length)

    chars = []
    count = 0
    for r in range(height):
        for c in range(width):
            if count < (length * 8) + 32:
                previous_length = len(chars)
                chars.extend(list(str(int2ba((img[r,c,0] & bits).item())).split('\'')[1]))
                chars.extend(list(str(int2ba((img[r,c,1] & bits).item())).split('\'')[1]))
                chars.extend(list(str(int2ba((img[r,c,2] & bits).item())).split('\'')[1]))
                count += len(chars) - previous_length
    output = bitarray("".join(chars))
    print(output.tobytes()[4:length + 4])

def hidden_image(image):
    img = imageio.imread(image)
    height, width, channels = img.shape
    print("Height:", height, "Width:", width, "Number of Channels:", channels)

    hidden_height = get_header(image, 0, 32, 1)
    hidden_width = get_header(image, 32, 32, 1)

    print("Hidden height:", hidden_height, "Hidden width:", hidden_width)
    
    count = 0
    chars = []
    for r in range(height):
        for c in range(width):
            if count < hidden_height * hidden_width * 32 + 64:
                chars.append(str(img[r,c,0] & 1))
                chars.append(str(img[r,c,1] & 1))
                chars.append(str(img[r,c,2] & 1))
                # If Alpha is used
                # chars.append(str(img[r,c,3] & 1))
                count += 3

    chars = chars[64:]
    # output = bitarray("".join(chars))
    # print(output)

    for r in range(hidden_height):
        for c in range(hidden_width):
            # print("R:", chars[0:8], "G:", chars[8:16], "B:", chars[16:24])

            red = ba2int(bitarray("".join(chars[0:8])))
            green = ba2int(bitarray("".join(chars[8:16])))
            blue = ba2int(bitarray("".join(chars[16:24])))
            # alpha = ba2int(bitarray("".join(chars[24:32])))

            # print("R:", red, "G:", green, "B:", blue)

            img[r,c][0] = red
            img[r,c][1] = green
            img[r,c][2] = blue
            # img[r,c][3] = alpha
            chars = chars[24:]

    imageio.imwrite("altered_py.png", img)

def detect_hidden(image):
    img = imageio.imread(image)
    height, width, channels = img.shape
    print("Height:", height, "Width:", width, "Number of Channels:", channels)

    for r in range(height):
        for c in range(width):
            red = '00000000' if (img[r,c,0] & 1) == 0 else '11111111'
            green = '00000000' if (img[r,c,1] & 1) == 0 else '11111111'
            blue = '00000000' if (img[r,c,2] & 1) == 0 else '11111111'

            img[r,c][0] = red
            img[r,c][1] = green
            img[r,c][2] = blue

    imageio.imwrite("detected_py.png", img)

if __name__ == "__main__":
    # text_with_header("sampleImages/hide_text.png", 3)
    # hidden_image("sampleImages/hide_image.png")
    detect_hidden("sampleImages/hide_image.png")