import numpy as np
import imageio
from bitarray import bitarray
from bitarray.util import ba2int, int2ba
import re

class arrayList:
    def __init__(self):
        self.data = np.zeros((100,), dtype=np.string_)
        self.capacity = 100
        self.size = 0

    def add(self, x):
        if self.size == self.capacity:
            self.capacity *= 4
            newdata = np.zeros((self.capacity,), dtype=np.string_)
            newdata[:self.size] = self.data
            self.data = newdata

        self.data[self.size] = x
        self.size += 1

    def remove(self, amount):
        self.data = self.data[amount:]
        self.size -= amount

    def get_data(self):
        return self.data[:self.size]

    def get_bytes(self):
        return np.reshape(self.data[:self.size], (-1, 8))

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
                # chars.extend(list(str(int2ba((img[r,c,0] & bits).item())).split('\'')[1]))
                # chars.extend(list(str(int2ba((img[r,c,1] & bits).item())).split('\'')[1]))
                chars.extend(list(str(int2ba((img[r,c,2] & bits).item())).split('\'')[1]))
                count += len(chars) - previous_length
    output = bitarray("".join(chars))
    print(output.tobytes())
    #print(ba2int(bitarray(output)))

def get_header(image, chans, header_start, header_length, bits):
    img = imageio.imread(image)
    height, width, _ = img.shape

    chars = []
    count = 0
    for r in range(height):
        for c in range(width):
            if count < header_start + header_length:
                previous_length = len(chars)
                if 0 in chans: chars.extend(list(str(int2ba((img[r,c,0] & bits).item())).split('\'')[1]))
                if 1 in chans: chars.extend(list(str(int2ba((img[r,c,1] & bits).item())).split('\'')[1]))
                if 2 in chans: chars.extend(list(str(int2ba((img[r,c,2] & bits).item())).split('\'')[1]))
                count += len(chars) - previous_length
    output = "".join(chars)[header_start:header_start + header_length]
    return ba2int(bitarray(output))

def text_with_header(image, chans, bits, testing_multiple):
    img = imageio.imread(image)
    height, width, _ = img.shape
    print("Height:", height, "Width:", width)

    length = get_header(image, chans, 0, 32, bits)
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
                if 0 in chans: chars.extend(list(str(int2ba((img[r,c,0] & bits).item())).split('\'')[1]))
                if 1 in chans: chars.extend(list(str(int2ba((img[r,c,1] & bits).item())).split('\'')[1]))
                if 2 in chans: chars.extend(list(str(int2ba((img[r,c,2] & bits).item())).split('\'')[1]))
                count += len(chars) - previous_length
    output = bitarray("".join(chars))
    print(output.tobytes()[4:length + 4])

def even_bits_text(image, chans, bits, testing_multiple):
    # Don't use 'bits'
    
    img = imageio.imread(image)
    height, width, _ = img.shape
    print("Height:", height, "Width:", width)

    length = get_header(image, chans, 0, 32, bits)
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

def hidden_image(image, chans, testing_multiple):
    img = imageio.imread(image)
    height, width, channels = img.shape
    print("Height:", height, "Width:", width, "Number of Channels:", channels)

    hidden_height = get_header(image, chans, 0, 32,1)
    hidden_width = get_header(image, chans, 32, 32,1)

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
                if 0 in chans: chars.append(str(img[r,c,0] & 1))
                if 1 in chans: chars.append(str(img[r,c,1] & 1))
                if 2 in chans: chars.append(str(img[r,c,2] & 1))
                if 3 in chans: chars.append(str(img[r,c,3] & 1))
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
            percent_done = ((r * hidden_width) + c) / (hidden_width * hidden_height)
            if percent_done % 10 == 0:
                print(percent_done, "percent done")

    print("100.0 percent done. Writing...")
    imageio.imwrite("altered_" + image, img)


def faster_hidden_image(image, chans, testing_multiple):
    img = imageio.imread(image)
    height, width, channels = img.shape
    print("Height:", height, "Width:", width, "Number of Channels:", channels)

    hidden_height = get_header(image, chans, 0, 32,1)
    hidden_width = get_header(image, chans, 32, 32,1)

    print("Hidden height:", hidden_height, "Hidden width:", hidden_width)

    if testing_multiple:
        if input("Continue?") in ["n", "N"]: 
            return

    chars = arrayList()
    for r in range(height):
        for c in range(width):
            if chars.size < hidden_height * hidden_width * 32 + 64:
                if 0 in chans: chars.add(str(img[r,c,0] & 1)) 
                if 1 in chans: chars.add(str(img[r,c,1] & 1))
                if 2 in chans: chars.add(str(img[r,c,2] & 1)) 
                if 3 in chans: chars.add(str(img[r,c,3] & 1))  

    chars.remove(64)
    chars = np.apply_along_axis(lambda x : ba2int(bitarray(b"".join(x))), 1, chars.get_bytes())
    img = np.reshape(chars[:hidden_width*hidden_height*3], (hidden_height, hidden_width, 3))
    print("Done, writing...")
    imageio.imwrite("fast_altered_" + image, img)


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

def get_flipped_header(image, header_start, header_length, bits):
    img = imageio.imread(image)
    height, width, _ = img.shape

    chars = []
    count = 0
    for c in range(width):
        for r in range(height):
            if count < header_start + header_length:
                previous_length = len(chars)
                chars.extend(list(str(int2ba((img[r,c,0] & bits).item())).split('\'')[1]))
                chars.extend(list(str(int2ba((img[r,c,1] & bits).item())).split('\'')[1]))
                chars.extend(list(str(int2ba((img[r,c,2] & bits).item())).split('\'')[1]))
                count += len(chars) - previous_length
    output = "".join(chars)[header_start:header_start + header_length]
    return ba2int(bitarray(output))

def flipped_text_with_header(image, bits, testing_multiple):
    img = imageio.imread(image)
    height, width, _ = img.shape
    print("Height:", height, "Width:", width)

    length = get_flipped_header(image, 0, 32, bits)
    print(length)
    
    if testing_multiple:
        if input("Continue?") in ["n", "N"]: 
            return

    chars = []
    count = 0
    for c in range(width):
        for r in range(height):
            if count < (length * 8) + 32:
                previous_length = len(chars)
                chars.extend(list(str(int2ba((img[r,c,0] & bits).item())).split('\'')[1]))
                chars.extend(list(str(int2ba((img[r,c,1] & bits).item())).split('\'')[1]))
                chars.extend(list(str(int2ba((img[r,c,2] & bits).item())).split('\'')[1]))
                count += len(chars) - previous_length
    output = bitarray("".join(chars))
    print(output.tobytes()[4:length + 4])

if __name__ == "__main__":
    images = ['WinkyFace', 'DogDog', 'Woof1', 'PupFriends', 'PuppyLeash', 'Brothers', 'WideDogIsWide', 'TheGrassIsGreener', 'MoJoJoJoCouch', 'Grooming',
    'LastBastionOfRadiance', 'Brothers_small', 'FriendlyPupper', 'GadgetRadiator', 'AlbumCover', 'TripleThreat', 'Gadget_tiny', 'Floof', 'Gadget_small',
    'Gadget_medium', 'ExtraCredit', 'Gadget', 'StegTest']

    hidden_image_sources = ['WinkyFace', 'TheGrassIsGreener', 'WideDogIsWide', 'MoJoJoJoCouch', 'Grooming', 'LastBastionOfRadiance']

    # TODO: fix even bits / 10
        # param that excludes certain values from being appended

    # for image in hidden_image_sources:
    #     print('Testing ' + image + ".png for hidden images")
    #     hidden_image("Images/" + image + ".png")

    # hidden_image("Images/Grooming.png")
    #TODO: flipped??
    # flipped_text_with_header("Images/TheGrassIsGreener.png", 1, False)
    # print(get_flipped_header("Images/TheGrassIsGreener.png", 0, 32, 1))
    # print(get_flipped_header("Images/TheGrassIsGreener.png", 32, 64, 1))

    # for image in hidden_image_sources:
    #     print('Getting headers for ' + image + ".png for hidden images")
    #     print(get_header("Images/" + image + ".png", 0, 32, 1))

    # text_with_header("Images/Grooming.png", 1, False)
    # read_n_bits("Images/Grooming.png", 1, 1000)

    # TODO: investigate
    # read_n_bits("Images/WinkyFace.png", 32, 256)
    # print(get_header("Images/WinkyFace.png", 0, 32, 32))
    faster_hidden_image("Images/Grooming.png", {1}, False)
    
    # for image in images:
    #     for bits in [1, 3, 7]:
    #         print('Testing ' + image + ".png with " + str(bits) + " bit representation")
    #         even_bits_text("Images/" + image + ".png", 1431655765, True)

    
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

    # TODO: look for image headers