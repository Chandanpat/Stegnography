import os
import wave
from essentials import *



def hide_text_in_audio(password):
    audio_file = input("Enter path of cover Audio: ")
    # audio_file= "./resources/audio_file.wav"
    message = bytes(input("Enter the text message to hide:"), "utf-8")
    output_file = input("Enter the name stego file with extension: ")
    # Open the audio file for reading
    audio = wave.open(audio_file, 'rb')
    frames = audio.readframes(-1)

    # Convert the message to binary
    # binary_message = ''.join(format(ord(char), '08b') for char in message)

    key = key_generator(password,'ta')
    # print(key)
    encrypted_message = encrypt(key, message,'ta')

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
    print("Text embedded successfully! Output file saved as: ", output_path)


# Function to extract a hidden text message from an audio file


def extract_text_from_audio(password):
    key,check = checkPass(password,'ta')
    if check == True:
        encoded_audio_file = input("Enter the path of the encoded audio file: ")
        # encoded_audio_file = "./output/encoded.wav"
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
        decrypted_message = decrypt(key, encrypted_message, 'ta')
        message = decrypted_message.decode("utf-8")
        print("\n\nMessage decoded from the stego file:- ", message)  # Print the extracted message as text
    else:
        print("Invalid Password!!")



def caller():
    while True:
        print("\n\t\tTEXT IN AUDIO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Text in Audio")  
        print("2. Decode Text from Audio")  
        print("3. Exit") 
        ch = int(input("\n\t\tEnter your choice: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            hide_text_in_audio(password) 

        elif ch == 2:
            password = input("Enter password for decryption:")
            extract_text_from_audio(password)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")


