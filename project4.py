import numpy as np
import imageio
import bitarray
from bitarray.util import ba2int

def text_with_header_least_sig(image):
    img = imageio.imread(image)
    height, width, _ = img.shape
    print("Height:", height, "Width:", width)

    chars = []
    count = 0
    for r in range(height):
        for c in range(width):
            if count < 32:
               chars.append(str(img[r,c,0] & 1))
               chars.append(str(img[r,c,1] & 1))
               chars.append(str(img[r,c,2] & 1))
               count += 3
    output = "".join(chars)[0:32]
    length = ba2int(bitarray.bitarray(output))
    print(length)

    chars = []
    count = 0
    for r in range(height):
        for c in range(width):
            if count < (length * 8) + 32:
                chars.append(str(img[r,c,0] & 1))
                chars.append(str(img[r,c,1] & 1))
                chars.append(str(img[r,c,2] & 1))
                count += 3
    output = bitarray.bitarray("".join(chars))
    print(output.tobytes()[4:length + 4])

if __name__ == "__main__":
    text_with_header_least_sig("sampleImages/hide_text.png")
    # 2 Least significants