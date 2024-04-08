from PIL import Image
from essentials import *
from calculations import *



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


def encode(password):
    image_to_hide_path = input("Enter path of image to be hidden: ")
    # image_to_hide_path = "./resources/secret.tiff"
    image_to_hide_in_path = input("Enter path to cover image: ")
    # image_to_hide_in_path = "./resources/input.tiff"
    encoded_image_path = "./output/"+input("Enter the name of stego file to be generated: ")
    n_bits = 1
    image_to_hide = Image.open(image_to_hide_path)
    image_to_hide_in = Image.open(image_to_hide_in_path)

    # Calculate required percentage
    # required_percentage = calculate_required_percentage_ii(image_to_hide_in.size, image_to_hide.size)
    # print(f"The secret image should occupy {required_percentage:.2f}% of the cover image.")


    width, height = image_to_hide.size
    hide_image = image_to_hide.load()
    hide_in_image = image_to_hide_in.load()

    data = []

    key = key_generator(password,'ii')
    # print(key)
    image_bytes = image_to_hide.tobytes()
    # print(image_bytes)
    encrypted_image = encrypt(key, image_bytes,'ii')

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
    
    make_image(data, image_to_hide.size).save(encoded_image_path)
    print("\n\nImage embedded successfully!! Stego file saved as: ",encoded_image_path)


def decode(password):
    key,check = checkPass(password,'ii')
    if check == True:
        encoded_image_path = input("Enter the path of Stego image: ")
        decoded_image_path = "./output/"+input("Enter the name of output file to be generated: ")
        n_bits = 1
        image_to_decode = Image.open(encoded_image_path)
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
        # Decrypt the image using the provided password
        decrypted_image_bytes = decrypted_image.tobytes()
        original_image_bytes = decrypt(key, decrypted_image_bytes,"ii")
        # Create a new image from the decrypted image bytes
        original_image = Image.frombytes("RGB", decrypted_image.size, original_image_bytes)
        original_image.save(decoded_image_path)
        print("\n\n\nImage extracted successfully! Output file saved as: ",decoded_image_path)
    else:
        print("Invalid Password!!")
        return 0


def caller():
    while True:
        print("\n\t\tIMAGE IN IMAGE STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Image in Image")  
        print("2. Decode Image from Image")  
        print("3. Exit") 
        ch = int(input("\n\t\t Enter your choice: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            encode(password)

        elif ch == 2:
            password = input("Enter password for decryption: ")
            decode(password)
            
        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")