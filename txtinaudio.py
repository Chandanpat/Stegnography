import os
import wave
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Function to hide a text message in an audio file


def encrypt(key, msg):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphered_data = cipher.encrypt(pad(msg, AES.block_size))
    # print(ciphered_data)
    with open('./output/encrypted_ta.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphered_data)
    return ciphered_data


def key_generator(password):
    simple_key = get_random_bytes(32)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('./output/key_ta.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key


def decrypt(key, cypherText):
    with open('./output/encrypted_ta.bin', 'rb') as f:
        iv = f.read(16)
        cypherText = f.read()
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        og = unpad(cipher.decrypt(cypherText), AES.block_size)
    return og



def hide_text_in_audio(audio_file, message, output_file,password):
    # Open the audio file for reading
    audio = wave.open(audio_file, 'rb')
    frames = audio.readframes(-1)

    # Convert the message to binary
    # binary_message = ''.join(format(ord(char), '08b') for char in message)

    key = key_generator(password)
    # print(key)
    encrypted_message = encrypt(key, message)

    # Check if the audio file can hold the message
    if len(encrypted_message) > len(frames) * 8:
        raise Exception("Message too long to hide in this audio file")

    # Hide the message in the least significant bit of each audio sample
    encoded_frames = bytearray(frames)
    message_index = 0
    for i in range(len(encoded_frames)):
        if message_index < len(encrypted_message):
            encoded_frames[i] = (encoded_frames[i] & 0xFE) | int(
                encrypted_message[message_index])
            message_index += 1

    # Get the script's directory and create the output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = script_dir + "\output"
    output_path = os.path.join(script_dir, output_file)

    # Write the encoded frames to the output file
    with wave.open(output_path, 'wb') as output:
        output.setparams(audio.getparams())
        output.writeframes(encoded_frames)

    print("Message hidden successfully! Output file saved as: ", output_path)


# Function to extract a hidden text message from an audio file


def extract_text_from_audio(encoded_audio_file, password):
    audio = wave.open(encoded_audio_file, 'rb')
    frames = audio.readframes(-1)

    # Initialize variables
    encrypted_message = ""
    message = ""
    consecutive_zeros = 0

    for frame in frames:
        # Extract the least significant bit
        bit = frame & 1
        encrypted_message += str(bit)

        # Check for consecutive zeros (end of message marker)
        if bit == 0:
            consecutive_zeros += 1
        else:
            consecutive_zeros = 0

        # If we have eight consecutive zeros, it's the end of the message
        if consecutive_zeros == 8:
            break

    # Remove the trailing zeros from the binary message
    # binary_message = binary_message[:-8]

    # Convert the binary message to text
    # for i in range(0, len(binary_message), 8):
    #     byte = binary_message[i:i + 8]
    #     message += chr(int(byte, 2))

    with open('./output/key_ta.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    # print(contents)
    password1 = contents[0]
    key = contents[1]
    # print(key)
    # print(str(password1, "utf-8"), "\n", password.strip())
    if str(password1, "utf-8") == password.strip():
        decrypted_message = decrypt(key, encrypted_message)
        message = decrypted_message.decode("utf-8")
        print("Extracted Message: ", message)  # Print the extracted message as text
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


    while True:
        print("\n\n\t1. Hide text in audio\n\t2. Retrieve text from audio\n\t3. Exit")
        ch = int(input("\n\t\tChoose from below options: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            audio_file= input("Enter path of cover Audio: ")
            # audio_file= "./resources/audio_file.wav"
            message=bytes(input("Enter the text message to hide:"), "utf-8")
            output_file = input("Enter the name stego file with extension: ")
            hide_text_in_audio(audio_file, message, output_file,password) 

        elif ch == 2:
            password = input("Enter password for decryption:")
            encoded_audio_file = input("Enter the path of the encoded audio file: ")
            # encoded_audio_file = "./output/encoded.wav"
            extract_text_from_audio(encoded_audio_file, password)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")


