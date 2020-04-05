import numpy as np
import imageio
from bitarray import bitarray
from bitarray.util import ba2int, int2ba
import re

def read_n_bits(image, bits, n):
    img = imageio.imread(image)
    height, width, _ = img.shape
    print("Height:", height, "Width:", width)

    chars = []
    count = 0
    for r in range(height):
        for c in range(width):
            if count < n:
                previous_length = len(chars)
                chars.extend(list(str(int2ba((img[r,c,0] & bits).item())).split('\'')[1]))
                chars.extend(list(str(int2ba((img[r,c,1] & bits).item())).split('\'')[1]))
                chars.extend(list(str(int2ba((img[r,c,2] & bits).item())).split('\'')[1]))
                count += len(chars) - previous_length
    output = bitarray("".join(chars))
    print(output.tobytes())
    #print(ba2int(bitarray(output)))

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

def text_with_header(image, bits, testing_multiple):
    img = imageio.imread(image)
    height, width, _ = img.shape
    print("Height:", height, "Width:", width)

    length = get_header(image, 0, 32, bits)
    print(length)
    
    if testing_multiple:
        if input("Continue?") in ["n", "N"]: 
            return

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

def even_bits_text(image, bits, testing_multiple):
    # Don't use 'bits'
    
    img = imageio.imread(image)
    height, width, _ = img.shape
    print("Height:", height, "Width:", width)

    length = get_header(image, 0, 32, bits)
    print(length)
    
    if testing_multiple:
        if input("Continue?") in ["n", "N"]: 
            return

    chars = []
    count = 0
    for r in range(height):
        for c in range(width):

            # change once we figure out headers
            if count<30:
                previous_length = len(chars)
                
                for color in range(3):
                    
                    print('color_before: ', (int2ba((img[r,c,color]).item())))
             
                    color_even=(list(str(int2ba((img[r,c,color]).item())).split('\'')[1]))

                    # to preserve leading 0's
                    if (len(color_even) < 8):
                        for i in range(8-len(color_even)):
                            color_even.insert(0,'0')
    
                    print('color_even: ', color_even)
                    for i in range(len(color_even)):
                        
                        if (i%2!=0):
                            print('added: ', color_even[i])
                            chars.extend(color_even[i]) 
                
                count += len(chars) - previous_length
    output = bitarray("".join(chars))
    print(output.tobytes()[4:length + 4])

def hidden_image(image, testing_multiple):
    img = imageio.imread(image)
    height, width, channels = img.shape
    print("Height:", height, "Width:", width, "Number of Channels:", channels)

    hidden_height = get_header(image, 0, 32,1)
    hidden_width = get_header(image, 32, 32,1)

    print("Hidden height:", hidden_height, "Hidden width:", hidden_width)

    if testing_multiple:
        if input("Continue?") in ["n", "N"]: 
            return

    count = 0
    chars = []
    for r in range(height):
        for c in range(width):
            if count < hidden_height * hidden_width * 32 + 64:
                previous_length = len(chars)
                chars.append(str(img[r,c,0] & 1))
                chars.append(str(img[r,c,1] & 1))
                chars.append(str(img[r,c,2] & 1))
                # If Alpha is used
                # chars.append(str(img[r,c,3] & 1))
                count += len(chars) - previous_length

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

    imageio.imwrite("altered_" + image + ".png", img)

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

    imageio.imwrite("detected_" + image, img)

if __name__ == "__main__":
    images = ['WinkyFace', 'DogDog', 'Woof1', 'PupFriends', 'PuppyLeash', 'Brothers', 'WideDogIsWide', 'TheGrassIsGreener', 'MoJoJoJoCouch', 'Grooming',
    'LastBastionOfRadiance', 'Brothers_small', 'FriendlyPupper', 'GadgetRadiator', 'AlbumCover', 'TripleThreat', 'Gadget_tiny', 'Floof', 'Gadget_small',
    'Gadget_medium', 'ExtraCredit', 'Gadget', 'StegTest']

    # TODO: fix even bits / 10

    sus_images = ['WideDogIsWide']
    for image in sus_images:
        print('Testing ' + image + ".png")
        hidden_image("Images/" + image + ".png", True)
        #for bits in [1, 3, 7]:
            #print('Testing ' + image + ".png with " + str(bits) + " bit representation")
            #even_bits_text("Images/" + image + ".png", 1431655765, True)

    
    # text_with_header("Images/PupFriends.png", 1)
    # text_with_header("Images/PuppyLeash.png", 1)

    # hidden_image("sampleImages/hide_image.png")
    # detect_hidden("sampleImages/hide_image.png")
    # read_n_bits("Images/WinkyFace.png", 7, 1800)
    # print(get_header("Images/WinkyFace.png", 0, 32, 1))
    # print(get_header("Images/DogDog.png", 0, 32, 1))
    # print(get_header("Images/Woof1.png", 0, 32, 1))
    # print(get_header("Images/PupFriends.png", 0, 32, 1))
    # print(get_header("Images/PuppyLeash.png", 0, 32, 1))
    # print(get_header("Images/Brothers.png", 0, 32, 1))
