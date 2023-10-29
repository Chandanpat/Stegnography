# watch the video for this project here: https://youtu.be/bZ88gnHzwz8

from PIL import Image
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def encrypt(key, data):
    # print(type(data))
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    # print(ciphered_data)
    with open('./output/encrypted.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphertext)
    return ciphertext


def key_generator(password):
    simple_key = get_random_bytes(32)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('./output/key.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key


def decrypt(key, cypherText):
    with open('./output/encrypted.bin', 'rb') as f:
        iv = f.read(16)
        cypherText = f.read()
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        og = unpad(cipher.decrypt(cypherText), AES.block_size)
    return og

MAX_COLOR_VALUE = 256
MAX_BIT_VALUE = 8

def make_image(data, resolution):
    image = Image.new("RGB", resolution)
    image.putdata(data)

    return image

def remove_n_least_significant_bits(value, n):
    value = value >> n 
    return value << n

def get_n_least_significant_bits(value, n):
    value = value << MAX_BIT_VALUE - n
    value = value % MAX_COLOR_VALUE
    return value >> MAX_BIT_VALUE - n

def get_n_most_significant_bits(value, n):
    return value >> MAX_BIT_VALUE - n

def shit_n_bits_to_8(value, n):
    return value << MAX_BIT_VALUE - n

# def encode(image_to_hide, image_to_hide_in, n_bits):

#     width, height = image_to_hide.size

#     hide_image = image_to_hide.load()
#     hide_in_image = image_to_hide_in.load()

#     data = []

#     for y in range(height):
#         for x in range(width):

#             # (107, 3, 10)
#             # most sig bits
#             r_hide, g_hide, b_hide = hide_image[x,y]

#             r_hide = get_n_most_significant_bits(r_hide, n_bits)
#             g_hide = get_n_most_significant_bits(g_hide, n_bits)
#             b_hide = get_n_most_significant_bits(b_hide, n_bits)

#             # remove lest n sig bits
#             r_hide_in, g_hide_in, b_hide_in = hide_in_image[x,y]

#             r_hide_in = remove_n_least_significant_bits(r_hide_in, n_bits)
#             g_hide_in = remove_n_least_significant_bits(g_hide_in, n_bits)
#             b_hide_in = remove_n_least_significant_bits(b_hide_in, n_bits)

#             data.append((r_hide + r_hide_in, 
#                          g_hide + g_hide_in,
#                          b_hide + b_hide_in))
            
#     print(data)
#     return make_image(data, image_to_hide.size)


def encode(image_to_hide, image_to_hide_in, n_bits, password):
    width, height = image_to_hide.size
    hide_image = image_to_hide.load()
    hide_in_image = image_to_hide_in.load()

    data = []

    key = key_generator(password)
    # print(key)
    image_bytes = image_to_hide.tobytes()
    # print(image_bytes)
    encrypted_image = encrypt(key, image_bytes)

    # Use an iterator for the encrypted image bytes
    encrypted_iterator = iter(encrypted_image)

    for y in range(height):
        for x in range(width):
            try:
                # Extract bytes from the encrypted image for each channel
                r_byte = next(encrypted_iterator)
                g_byte = next(encrypted_iterator)
                b_byte = next(encrypted_iterator)

                # Extract the n most significant bits
                r_hide_pixel = get_n_most_significant_bits(r_byte, n_bits)
                g_hide_pixel = get_n_most_significant_bits(g_byte, n_bits)
                b_hide_pixel = get_n_most_significant_bits(b_byte, n_bits)

                # Remove the least n significant bits from the cover image
                r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]
                r_hide_in = remove_n_least_significant_bits(r_hide_in, n_bits)
                g_hide_in = remove_n_least_significant_bits(g_hide_in, n_bits)
                b_hide_in = remove_n_least_significant_bits(b_hide_in, n_bits)

                data.append((r_hide_pixel + r_hide_in, g_hide_pixel + g_hide_in, b_hide_pixel + b_hide_in))
            except StopIteration:
                # If there's no more data in the encrypted image, break the loop
                break
    
    return make_image(data, image_to_hide.size)


def decode(image_to_decode, n_bits, password):
    width, height = image_to_decode.size
    encoded_image = image_to_decode.load()

    data = []

    for y in range(height):
        for x in range(width):
            r_encoded, g_encoded, b_encoded = encoded_image[x, y]

            r_encoded = get_n_least_significant_bits(r_encoded, n_bits)
            g_encoded = get_n_least_significant_bits(g_encoded, n_bits)
            b_encoded = get_n_least_significant_bits(b_encoded, n_bits)

            r_encoded = shit_n_bits_to_8(r_encoded, n_bits)
            g_encoded = shit_n_bits_to_8(g_encoded, n_bits)
            b_encoded = shit_n_bits_to_8(b_encoded, n_bits)

            data.append((r_encoded, g_encoded, b_encoded))

    decrypted_image = make_image(data, image_to_decode.size)


    with open('./output/key.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    # print(contents)
    password1 = contents[0]
    key = contents[1]
    # print(key)
    # print(str(password1, "utf-8"), "\n", password.strip())
    if str(password1, "utf-8") == password.strip():
        # Decrypt the image using the provided password
        decrypted_image_bytes = decrypted_image.tobytes()
        original_image_bytes = decrypt(key, decrypted_image_bytes)
        # print(original_image_bytes)

        # Create a new image from the decrypted image bytes
        original_image = Image.frombytes("RGB", decrypted_image.size, original_image_bytes)
        return original_image

    else:
        print("Invalid Password!!")
        return 0

    




    


def caller():
    # image_to_hide_path = input("Enter path of image to be hidden: ")
    # image_to_hide_in_path = r"D:\VIT\Major_Project\Stegnography\input.tiff"
    # image_to_hide_in_path = input("Enter path to cover image: ")
    # encoded_image_path = "./output/encoded.tiff"
    # encoded_image_path = input("Enter path to encoded image: ")
    # decoded_image_path = "./output/decoded.tiff"
    # n_bits = 1
    # print("end")

    # image_to_hide = Image.open(image_to_hide_path)
    # image_to_hide_in = Image.open(image_to_hide_in_path)
    # encode(image_to_hide, image_to_hide_in, n_bits).save(encoded_image_path)
    
    # image_to_decode = Image.open(encoded_image_path)
    # decode(image_to_decode, n_bits).save(decoded_image_path)



    while True:
        print("\n\n\t1. Hide Image in image\n\t2. Retrieve Image from image\n\t3. Exit")
        ch = int(input("\n\t\t Enter your choice: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            image_to_hide_path = input("Enter path of image to be hidden: ")
            # image_to_hide_path = "./resources/secret.tiff"
            image_to_hide_in_path = input("Enter path to cover image: ")
            # image_to_hide_in_path = "./resources/input.tiff"
            encoded_image_path = "./output/encoded.tiff"
            n_bits = 1

            image_to_hide = Image.open(image_to_hide_path)
            image_to_hide_in = Image.open(image_to_hide_in_path)
            encode(image_to_hide, image_to_hide_in, n_bits, password).save(encoded_image_path)
            print("\n\nImage embedded successfully!! Check encoded.tiff and use it for retrieving original image.")

        elif ch == 2:
            password = input("Enter password for encryption: ")
            encoded_image_path = input("Enter path to encoded image: ")
            decoded_image_path = "./output/decoded.tiff"
            n_bits = 1

            image_to_decode = Image.open(encoded_image_path)
            decode(image_to_decode, n_bits, password).save(decoded_image_path)
            print("\n\nImage retrieved successfully!! decoded.tiff is your original image.")

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")