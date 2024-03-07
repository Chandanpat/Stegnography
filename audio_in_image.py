from PIL import Image
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import wave


def encrypt(key, data):
    # print(type(data))
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    # print(ciphered_data)
    with open('./output/encrypted_ai.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphertext)
    return ciphertext


def key_generator(password):
    simple_key = get_random_bytes(32)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('./output/key_ai.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key


def decrypt(key, cypherText):
    with open('./output/encrypted_ai.bin', 'rb') as f:
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


def encode(password):
    # image_to_hide_path = input("Enter path of audio to be hidden: ")
    audio_to_hide_path = "./resources/audio_file3.wav"
    # image_to_hide_in_path = input("Enter path of cover image: ")
    image_to_hide_in_path = "./resources/download (1).jpeg"
    # encoded_image_path = "./output/"+input("Enter the name of stego file to be generated: ")
    encoded_image_path = "./output/image_output.jpg"
    n_bits = 1
    image_to_hide_in = Image.open(image_to_hide_in_path)
    width, height = image_to_hide_in.size
    hide_in_image = image_to_hide_in.load()

    # Open the secret audio file for reading
    with wave.open(audio_to_hide_path, 'rb') as secret_audio_file:
        secret_frames = secret_audio_file.readframes(-1)

    # Encrypt the secret audio data
    key = key_generator(password)
    encrypted_audio = encrypt(key, secret_frames)

    data = []

    a = 0
    b = 0

    # Use an iterator for the encrypted image bytes
    encrypted_iterator = iter(encrypted_audio)
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
                break
            a+=1
        b+=1


    for y in range(b,height):
        for x in range(a,width):
            r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]
            data.append((r_hide_in, g_hide_in, b_hide_in))

    
    make_image(data, image_to_hide_in.size).save(encoded_image_path)
    print("\n\nStego file has successfully generated. Use ",encoded_image_path," for decoding")


# def decode(password):
#     # encoded_image_path = input("Enter the path of encoded audio: ")
#     encoded_image_path = "./output/image_output.jpg"
#     # decoded_image_path = "./output/"+input("Enter the name of output file to be generated: ")
#     decoded_image_path = "./output/output_audio.wav"
#     n_bits = 1
#     image_to_decode = Image.open(encoded_image_path)
#     width, height = image_to_decode.size
#     encoded_image = image_to_decode.load()

#     data = []

#     for y in range(height):
#         for x in range(width):
#             r_encoded, g_encoded, b_encoded = encoded_image[x, y]

#             r_encoded = get_n_least_significant_bits(r_encoded, n_bits)
#             g_encoded = get_n_least_significant_bits(g_encoded, n_bits)
#             b_encoded = get_n_least_significant_bits(b_encoded, n_bits)

#             r_encoded = shit_n_bits_to_8(r_encoded, n_bits)
#             g_encoded = shit_n_bits_to_8(g_encoded, n_bits)
#             b_encoded = shit_n_bits_to_8(b_encoded, n_bits)

#             data.append((r_encoded, g_encoded, b_encoded))

#     decrypted_image = make_image(data, image_to_decode.size)


#     with open('./output/key_ii.bin', 'rb') as f:
#         data = f.read()
#     contents = data.splitlines()
#     # print(contents)
#     password1 = contents[0]
#     key = contents[1]
#     # print(key)
#     # print(str(password1, "utf-8"), "\n", password.strip())
#     if str(password1, "utf-8") == password.strip():
#         # Decrypt the image using the provided password
#         decrypted_image_bytes = decrypted_image.tobytes()
#         original_image_bytes = decrypt(key, decrypted_image_bytes)
#         # print(original_image_bytes)

#         # Create a new image from the decrypted image bytes
#         original_image = Image.frombytes("RGB", decrypted_image.size, original_image_bytes)
#         original_image.save(decoded_image_path)

#     else:
#         print("Invalid Password!!")
#         return 0

def shift_n_bits_to_8(value, n_bits):
    return value << (8 - n_bits)
def decode(password):
    encoded_image_path = "./output/image_output.jpg"
    decoded_audio_path = "./output/output_audio.wav"
    n_bits = 1

    # Open the stego image for decoding
    image_to_decode = Image.open(encoded_image_path)
    width, height = image_to_decode.size
    encoded_image = image_to_decode.load()

    # List to store extracted audio frames
    extracted_audio_frames = bytearray()

    # Iterate through each pixel in the image
    for y in range(height):
        for x in range(width):
            r_encoded, g_encoded, b_encoded = encoded_image[x, y]

            # Extract the least significant bits
            r_encoded = get_n_least_significant_bits(r_encoded, n_bits)
            g_encoded = get_n_least_significant_bits(g_encoded, n_bits)
            b_encoded = get_n_least_significant_bits(b_encoded, n_bits)

            # Shift the bits to reconstruct the original byte
            r_encoded = shift_n_bits_to_8(r_encoded, n_bits)
            g_encoded = shift_n_bits_to_8(g_encoded, n_bits)
            b_encoded = shift_n_bits_to_8(b_encoded, n_bits)

            # Append the reconstructed byte to the extracted audio frames
            extracted_audio_frames.append(r_encoded)
            extracted_audio_frames.append(g_encoded)
            extracted_audio_frames.append(b_encoded)



    with open('./output/key_ai.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    password1 = contents[0]
    key = contents[1]

    # Verify password
    if str(password1, "utf-8") == password.strip():
        # Decrypt the encrypted audio
        decrypted_audio = decrypt(key, extracted_audio_frames)

        # Write the decrypted audio to the output file
        with wave.open(decoded_audio_path, 'wb') as output_audio_file:
            output_audio_file.setframerate(22050)
            output_audio_file.writeframes(decrypted_audio)

        print("Audio extracted successfully! Output file saved as:", decoded_audio_path)
    else:
        print("Invalid Password!!")


    print("Audio extracted successfully! Output file saved as:", decoded_audio_path)

def main():

    while True:
        print("\n\n\t1. Hide Audio in image\n\t2. Retrieve Audio from image\n\t3. Exit")
        ch = int(input("\n\t\t Enter your choice: \n"))

        if ch == 1:
            # password = input("Enter password for encryption: ")
            password = "qwerty@1234567890"
            encode(password)

        elif ch == 2:
            password = input("Enter password for decryption: ")
            decode(password)
            
        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")


if __name__ == "__main__":
    main()
