import os
import wave
from PIL import Image
from essentials import *



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



def hide_image_in_audio(password):
    audio_file= input("Enter path of cover Audio: ")
    # audio_file= "./resources/Audio_test.wav"
    image_to_hide_path = input("Enter path of image to be hidden: ")
    # image_to_hide_path = "./resources/parrot.jpg"
    image = Image.open(image_to_hide_path)
    output_file = input("Enter the name stego file with extension to be generated: ")
    # output_file = "output_test.wav"
    # Open the audio file for reading
    audio = wave.open(audio_file, 'rb')
    frames = audio.readframes(-1)

    # Convert the message to binary
    # binary_message = ''.join(format(ord(char), '08b') for char in message)

    key = key_generator(password, 'ia')
    # print(key)
    image_bytes = image.tobytes()
    # print(image_bytes)
    encrypted_image = encrypt(key, image_bytes, 'ia')

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

    print("\n\n\nImage embedded successfully! Stego file saved as: ", output_path)

    return gap_size, image.size


# Function to extract a hidden text message from an audio file


def extract_text_from_audio(password, gap_index, size):
    key,check = checkPass(password,'ia')
    if check == True:
        encoded_audio_file = input("Enter the path of the Stego audio: ")
        # encoded_audio_file = "./output/output_test.wav"
        decoded_image_path = "./output/"+input("Enter the name of output file to be generated: ")
        # encoded_audio_file = "./output/encoded.wav"
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
        decrypted_image_bytes = decrypt(key, encrypted_image, "ia")
        Image.frombytes("RGB", size, decrypted_image_bytes).save(decoded_image_path)
        print("\n\n\nImage extracted successfully! Output file saved as: ", decoded_image_path)
    else:
        print("Invalid Password!!")



def caller():
    gap_size = 0
    while True:
        print("\n\t\tIMAGE IN AUDIO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Image in Audio")  
        print("2. Decode Image from Audio")  
        print("3. Exit")
        ch = int(input("\n\t\tChoose from below options: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            gap_size,size = hide_image_in_audio(password) 

        elif ch == 2:
            password = input("Enter password for decryption: ")
            extract_text_from_audio(password, gap_size, size)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")



