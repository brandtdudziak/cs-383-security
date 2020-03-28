import numpy as np
import imageio
import bitarray

def text():
    img = imageio.imread("sampleImages/hide_text.png")
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
               count += 1
    output = "".join(chars)
    length = output[0:32]
    print(length + "\n")

    chars = []
    count = 0
    for r in range(height):
        for c in range(width):
            if count < 1600:
                chars.append(str(img[r,c,0] & 1))
                chars.append(str(img[r,c,1] & 1))
                chars.append(str(img[r,c,2] & 1))
                count += 1
    output = bitarray.bitarray("".join(chars))
    print(output.tobytes()[4:573])

if __name__ == "__main__":
    text()