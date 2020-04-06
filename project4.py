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

    def remove_from_end(self, amount):
        self.data = self.data[:-amount]
        self.size -= amount

    def get_data(self):
        return self.data[:self.size]

    def get_bytes(self):
        return np.reshape(self.data[:self.size], (-1, 8))

def read_n_bits(image, chans, bits, n):
    img = imageio.imread(image)
    height, width, _ = img.shape
    print("Height:", height, "Width:", width)

    chars = []
    count = 0
    for r in range(height):
        for c in range(width):
            if count < n:
                previous_length = len(chars)
                if 0 in chans: chars.extend(list(str(int2ba((img[r,c,0] & bits).item())).split('\'')[1]))
                if 1 in chans: chars.extend(list(str(int2ba((img[r,c,1] & bits).item())).split('\'')[1]))
                if 2 in chans: chars.extend(list(str(int2ba((img[r,c,2] & bits).item())).split('\'')[1]))
                if 3 in chans: chars.extend(list(str(int2ba((img[r,c,3] & bits).item())).split('\'')[1]))
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
            if len(chars) < header_start + header_length:
                for chan in chans:
                    chars.append(str(img[r,c,chan] & 1)) 
    output = "".join(chars)[header_start:header_start + header_length]
    return ba2int(bitarray(output))

def text_with_header(image, bit_start, chans, bits, testing_multiple):
    img = imageio.imread(image)
    height, width, channels = img.shape
    print("Height:", height, "Width:", width, "Number of Channels:", channels)

    if len(chans) > channels: 
        print("Too many channels")
        return 

    length = get_header(image, chans, bit_start, 32, bits)
    print(length)
    # print(hidden_width)
    
    if testing_multiple:
        if input("Continue?") in ["n", "N"]: 
            return

    chars = []
    count = 0
    for r in range(height):
        for c in range(width):
            if count < (length * 8) + 32 + bit_start:
                previous_length = len(chars)
                if 0 in chans: chars.extend(list(str(int2ba((img[r,c,0] & bits).item())).split('\'')[1]))
                if 1 in chans: chars.extend(list(str(int2ba((img[r,c,1] & bits).item())).split('\'')[1]))
                if 2 in chans: chars.extend(list(str(int2ba((img[r,c,2] & bits).item())).split('\'')[1]))
                if 3 in chans: chars.extend(list(str(int2ba((img[r,c,3] & bits).item())).split('\'')[1]))
                count += len(chars) - previous_length
    output = bitarray("".join(chars))[bit_start:bit_start+(length*8+32)]
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

def faster_hidden_image(image, bit_start, chans, testing_multiple):
    img = imageio.imread(image)
    height, width, channels = img.shape
    print("Height:", height, "Width:", width, "Number of Channels:", channels)

    hidden_height = get_header(image, chans, bit_start, 32,1)
    hidden_width = get_header(image, chans, bit_start+32, 32,1)

    print("Hidden height:", hidden_height, "Hidden width:", hidden_width)

    if testing_multiple:
        if input("Continue?") in ["n", "N"]: 
            return

    chars = arrayList()
    for r in range(height):
        for c in range(width):
            if chars.size < hidden_height * hidden_width * 32 + 64 + bit_start:
                for chan in chans:
                    chars.add(str(img[r,c,chan] & 1)) 


    print("Done gathering bits. Generating image:")
    chars.remove(64 + bit_start)
    if chars.size%8!=0: chars.remove_from_end(chars.size%8)
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

def get_flipped_header(image, chans, header_start, header_length, bits):
    img = imageio.imread(image)
    height, width, _ = img.shape

    chars = []
    count = 0
    for c in range(width):
        for r in range(height):
            if len(chars) < header_start + header_length:
                for chan in chans:
                    chars.extend(list(str(int2ba((img[r,c,chan] & bits).item())).split('\'')[1]))
    output = "".join(chars)[header_start:header_start + header_length]
    return ba2int(bitarray(output))

def flipped_text_with_header(image, bit_start, chans, bits, testing_multiple):
    img = imageio.imread(image)
    height, width, _ = img.shape
    print("Height:", height, "Width:", width)

    length = get_flipped_header(image, chans,bit_start, 32, bits)
    # width = get_flipped_header(image,chans,32,32,bits)
    print(length)
    # print(width)
    
    if testing_multiple:
        if input("Continue?") in ["n", "N"]: 
            return

    chars = []
    for c in range(width):
        for r in range(height):
            if len(chars) < (length * 8) + 32 + bit_start:
                for chan in chans:
                    chars.extend(list(str(int2ba((img[r,c,chan] & bits).item())).split('\'')[1]))
    output = bitarray("".join(chars))
    print(output.tobytes()[bit_start + 4 : bit_start + length + 4])

def flipped_faster_hidden_image(image, bit_start, chans, testing_multiple):
    img = imageio.imread(image)
    height, width, channels = img.shape
    print("Height:", height, "Width:", width, "Number of Channels:", channels)

    hidden_height = get_flipped_header(image, chans, bit_start, 32,1)
    hidden_width = get_flipped_header(image, chans, bit_start+32, 32,1)

    print("Hidden height:", hidden_height, "Hidden width:", hidden_width)

    if testing_multiple:
        if input("Continue?") in ["n", "N"]: 
            return

    chars = arrayList()
    for c in range(width):
        for r in range(height):
            if chars.size < hidden_height * hidden_width * 32 + 64 + bit_start:
                if 0 in chans: chars.add(str(img[r,c,0] & 1)) 
                if 1 in chans: chars.add(str(img[r,c,1] & 1))
                if 2 in chans: chars.add(str(img[r,c,2] & 1)) 
                if 3 in chans: chars.add(str(img[r,c,3] & 1))


    print("Done gathering bits. Generating image:")
    chars.remove(64 + bit_start)
    if chars.size%8!=0: chars.remove_from_end(chars.size%8)
    chars = np.apply_along_axis(lambda x : ba2int(bitarray(b"".join(x))), 1, chars.get_bytes())
    #TODO: construct only green
    print(chars)
    chars = np.insert(chars, chars[::3], 0, 0)
    # for i in range(len(chars)):
    #     if i % 3 != 1: chars = np.insert(chars, i, 0)
    #     if i % 1000 == 0: print(i)
    print(chars)
    # img = np.reshape(chars[:hidden_width*hidden_height*3*3], (hidden_height*3, hidden_width, 3))
    # print("Done, writing...")
    # imageio.imwrite("fast_altered_" + image, img)

if __name__ == "__main__":
    images = ['WinkyFace', 'DogDog', 'Woof1', 'PupFriends', 'PuppyLeash', 'Brothers', 'WideDogIsWide', 'TheGrassIsGreener', 'MoJoJoJoCouch', 'Grooming',
    'LastBastionOfRadiance', 'Brothers_small', 'FriendlyPupper', 'GadgetRadiator', 'AlbumCover', 'TripleThreat', 'Gadget_tiny', 'Floof', 'Gadget_small',
    'Gadget_medium', 'ExtraCredit', 'Gadget', 'StegTest']

    hidden_image_sources = ['WinkyFace', 'TheGrassIsGreener', 'WideDogIsWide', 'MoJoJoJoCouch', 'Grooming', 'LastBastionOfRadiance']

    # TODO: fix even bits / 10
        # param that excludes certain values from being appended

    # text_with_header("Images/Brothers_found.png", 0, {1}, 1, True)

    # faster_hidden_image("Images/WideDogIsWide.png", 1000, {0,1,2}, True)
    # flipped_faster_hidden_image("Images/TheGrassIsGreener.png", 0, {0,1,2}, True)

    # TODO: can't get this to be what Carol got
    text_with_header("fast_altered_Images/WideDogIsWide.png", 0, [0], 1, True)
    # faster_hidden_image("Images/PupFriends.png", 0, [2,1,0], True)

    #TODO: test Bothers_found
    # print("Testing RGB combinations on Grooming_found")
    # for channel_comb in [[0,1,2],[0,1],[0,2],[1,2],[0],[1],[2], [0,2,1], [1,0,2],[1,0], [1,2,0],[2,0], [2,1,0],[2,1], [2,0,1]]:
    #     for bit_start in [0, 1000]:
    #         print("Channel combination:",channel_comb, "Bit Start:", bit_start)
    #         flipped_text_with_header("Images/Grooming_found.png", bit_start, channel_comb, 1, True)

    # for image in images:
    #     print('Testing ' + image + ".png for hidden text with all channels")
    #     text_with_header("Images/" + image + ".png", 1000, {0,1,2,3}, 1, True)

    # for image in hidden_image_sources:
    #     print('Testing ' + image + ".png for hidden images")
    #     hidden_image("Images/" + image + ".png")

    # text_with_header("fast_alteted_Images/TheGrassIsGreener.png",0, {0}, 1, True)

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
    # faster_hidden_image("Images/Brothers_found.png", {0}, True)
    # detect_hidden("Images/Brothers_found.png")
    # print(get_header("Images/Gadget.png", {0,1,2,3}, 0, 32, 1))
    
    # text_with_header("fast_altered_Images/TheGrassIsGreener.png",{0,2},0,1, True)
    # images = ['WideDogIsWide']

    # for image in images:
        
    #     print('Testing ' + image + ".png")
    #     flipped_faster_hidden_image("Images/" + image + ".png",1000,{0,1,2}, True)
    # flipped_text_with_header("Images/GadgetRadiator.png",{0,1,2}, 1, True)
    # flipped_text_with_header("Images/TheGrassIsGreener.png", 1, True)
    # flipped_faster_hidden_image("Images/TheGrassIsGreener.png",0,{0,1,2},True)
    # flipped_faster_hidden_image("fast_altered_Images/TheGrassIsGreener.png",0,{0,1,2}, True)
    # detect_hidden("fast_altered_Images/TheGrassIsGreener.png")
    # detect_hidden("fast_altered_Images/MoJoJoJoCouch.png")
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