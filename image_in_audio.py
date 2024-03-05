import os
import wave
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import numpy as np


def encrypt(key, data):
    # print(type(data))
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    # print(ciphered_data)
    with open('./output/encrypted_ia.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphertext)
    return ciphertext


def key_generator(password):
    simple_key = get_random_bytes(32)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('./output/key_ia.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key


def decrypt(key, cypherText):
    with open('./output/encrypted_ia.bin', 'rb') as f:
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




# def hide_image_in_audio(audio_file, image, output_file,password):
#     # Open the audio file for reading
#     audio = wave.open(audio_file, 'rb')
#     frames = audio.readframes(-1)

#     # Convert the message to binary
#     # binary_message = ''.join(format(ord(char), '08b') for char in message)

#     key = key_generator(password)
#     # print(key)
#     image_bytes = image.tobytes()
#     # print(image_bytes)
#     encrypted_image = encrypt(key, image_bytes)

#     # Check if the audio file can hold the message
#     if len(encrypted_image) > len(frames) * 8:
#         raise Exception("Message too long to hide in this audio file")

#     # Hide the message in the least significant bit of each audio sample
#     encoded_frames = bytearray(frames)
#     message_index = 0
#     for i in range(len(encoded_frames)):
#         if message_index < len(encrypted_image):
#             encoded_frames[i] = (encoded_frames[i] & 0xFE) | int(
#                 encrypted_image[message_index])
#             message_index += 1

#     # Get the script's directory and create the output path
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     script_dir = script_dir + "\output"
#     output_path = os.path.join(script_dir, output_file)

#     # Write the encoded frames to the output file
#     with wave.open(output_path, 'wb') as output:
#         output.setparams(audio.getparams())
#         output.writeframes(encoded_frames)

#     print("Image hidden successfully! Output file saved as: ", output_path)


def hide_image_in_audio(audio_file, image, output_file,password):
    # Open the audio file for reading
    audio = wave.open(audio_file, 'rb')
    frames = audio.readframes(-1)

    # Convert the message to binary
    # binary_message = ''.join(format(ord(char), '08b') for char in message)

    key = key_generator(password)
    # print(key)
    image_bytes = image.tobytes()
    # print(image_bytes)
    encrypted_image = encrypt(key, image_bytes)

    # Check if the audio file can hold the message
    if len(encrypted_image) > len(frames) * 8:
        raise Exception("Message too long to hide in this audio file")

    # Hide the message in the least significant bit of each audio sample
    # Calculate the gap size based on the number of frames in the audio file and the length of the encrypted image


    # Hide the encrypted image in the least significant bit of audio samples with a gap
    encoded_frames = bytearray(frames)
    message_index = 0

    total_frames = len(encoded_frames)
    encrypted_image_size = len(encrypted_image)
    gap_size = max(1, total_frames // encrypted_image_size)

    for i in range(0, len(encoded_frames), gap_size):
        if message_index < len(encrypted_image):
            encoded_frames[i] = (encoded_frames[i] & 0xFE) | int(encrypted_image[message_index])
            message_index += 1


    # Get the script's directory and create the output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = script_dir + "\output"
    output_path = os.path.join(script_dir, output_file)

    # Write the encoded frames to the output file
    with wave.open(output_path, 'wb') as output:
        output.setparams(audio.getparams())
        output.writeframes(encoded_frames)

    print("Image hidden successfully! Output file saved as: ", output_path)

    return gap_size


# Function to extract a hidden text message from an audio file


def extract_text_from_audio(encoded_audio_file, decoded_image_path, password, gap_index, size):
    audio = wave.open(encoded_audio_file, 'rb')
    frames = audio.readframes(-1)

    # Initialize variables
    encrypted_image = ""
    message = ""
    consecutive_zeros = 0

    for i in range(0, len(frames), gap_index):
        frame = frames[i]

        # Extract the least significant bit
        bit = frame & 1
        encrypted_image += str(bit)

        # Check for consecutive zeros (end of message marker)
        if bit == 0:
            consecutive_zeros += 1
        else:
            consecutive_zeros = 0

        # If we have eight consecutive zeros, it's the end of the message
        if consecutive_zeros == 8:
            break

    # Remove the trailing zeros from the binary message
    encrypted_image = encrypted_image[:-(consecutive_zeros)]

    # Read the encryption key from the file
    with open('./output/key_ia.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    password1 = contents[0]
    key = contents[1]

    # Verify password
    if str(password1, "utf-8") == password.strip():
        # decrypted_image_bytes = encrypted_image.tobytes()
        decrypted_image_bytes = decrypt(key, encrypted_image)
        Image.frombytes("RGB", size, decrypted_image_bytes).save(decoded_image_path)
        print("Image extracted successfully! Output file saved as: ", decoded_image_path)
    else:
        print("Invalid Password!!")

# Main function


def caller():
    # choice = input("Enter 1 for encryption or 2 for decryption: ")

    # if choice == '1':
    #     audio_file = input("Enter the path of the audio file: ")
    #     message = input("Enter the text message to hide: ")
    #     output_file = input(
    #         "Enter the output file name (e.g., encoded_audio.wav): ")
    #     hide_text_in_audio(audio_file, message, output_file)
    # elif choice == '2':
    #     encoded_audio_file = input(
    #         "Enter the path of the encoded audio file: ")
    #     extracted_message = extract_text_from_audio(encoded_audio_file)
        
    # else:
    #     print("Invalid choice. Please enter 1 for encryption or 2 for decryption.")

    gap_size = 0
    while True:
        print("\n\n\t1. Hide image in audio\n\t2. Retrieve image from audio\n\t3. Exit")
        ch = int(input("\n\t\tChoose from below options: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            audio_file= input("Enter path of cover Audio: ")
            # audio_file= "./resources/Audio_test.wav"
            image_to_hide_path = input("Enter path of image to be hidden: ")
            # image_to_hide_path = "./resources/parrot.jpg"
            image_to_hide = Image.open(image_to_hide_path)
            # output_file = input("Enter the name stego file with extension: ")
            output_file = "output_test.wav"
            gap_size = hide_image_in_audio(audio_file, image_to_hide, output_file,password) 

        elif ch == 2:
            password = input("Enter password for decryption:")
            encoded_audio_file = input("Enter the path of the encoded audio file: ")
            # encoded_audio_file = "./output/output_test.wav"
            decoded_image_path = "./output/decoded_test.jpg"
            # encoded_audio_file = "./output/encoded.wav"
            extract_text_from_audio(encoded_audio_file, decoded_image_path, password, gap_size, image_to_hide.size)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")



