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
    with open('./output/encrypted_aa.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphertext)
    return ciphertext


def key_generator(password):
    simple_key = get_random_bytes(32)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('./output/key_aa.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key


def decrypt(key, cypherText):
    with open('./output/encrypted_aa.bin', 'rb') as f:
        iv = f.read(16)
        cypherText = f.read()
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        og = unpad(cipher.decrypt(cypherText), AES.block_size)
    return og




def hide_audio_in_audio(cover_audio, secret_audio, output_file, password):
    # Open the cover audio file for reading
    with wave.open(cover_audio, 'rb') as cover_audio_file:
        cover_frames = cover_audio_file.readframes(-1)

    # Open the secret audio file for reading
    with wave.open(secret_audio, 'rb') as secret_audio_file:
        secret_frames = secret_audio_file.readframes(-1)

    # Encrypt the secret audio data
    key = key_generator(password)
    encrypted_audio = encrypt(key, secret_frames)

    # Pad the encrypted audio if it's shorter than the cover audio
    if len(encrypted_audio) < len(cover_frames):
        encrypted_audio += b'\0' * (len(cover_frames) - len(encrypted_audio))

    # Embed the encrypted audio into the cover audio frames
    encoded_frames = bytearray(cover_frames)
    for i in range(len(encrypted_audio)):
        encoded_frames[i] = (encoded_frames[i] & 0xFE) | (encrypted_audio[i] >> 7)

    # Write the encoded frames to the output file
    with wave.open(output_file, 'wb') as output:
        output.setparams(cover_audio_file.getparams())
        output.writeframes(encoded_frames)

    print("Audio hidden successfully! Output file saved as:", output_file)

    


def extract_audio_from_audio(encoded_audio_file, decoded_audio_path, password):
    # Open the encoded audio file for reading
    with wave.open(encoded_audio_file, 'rb') as audio_file:
        frames = audio_file.readframes(-1)

    # Initialize variables
    encrypted_audio = b""
    consecutive_zeros = 0

    for frame in frames:
        # Extract the least significant bit
        bit = frame & 1
        encrypted_audio += bytes([bit])

        # Check for consecutive zeros (end of message marker)
        if bit == 0:
            consecutive_zeros += 1
        else:
            consecutive_zeros = 0

        # If we have eight consecutive zeros, it's the end of the encrypted audio
        if consecutive_zeros == 8:
            break

    # Remove the trailing zeros from the encrypted audio
    encrypted_audio = encrypted_audio[:-(consecutive_zeros)]

    # Read the encryption key from the file
    with open('./output/key_aa.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    password1 = contents[0]
    key = contents[1]

    # Verify password
    if str(password1, "utf-8") == password.strip():
        # Decrypt the encrypted audio
        decrypted_audio_bytes = decrypt(key, encrypted_audio)

        # Write the decrypted audio to the output file
        with wave.open(decoded_audio_path, 'wb') as output_audio_file:
            output_audio_file.setparams(audio_file.getparams())
            output_audio_file.setframerate(22050)
            output_audio_file.writeframes(decrypted_audio_bytes)

        print("Audio extracted successfully! Output file saved as:", decoded_audio_path)
    else:
        print("Invalid Password!!")




# Main function
def caller():
    while True:
        print("\n\n\t1. Hide audio in audio\n\t2. Retrieve audio from audio\n\t3. Exit")
        ch = int(input("\n\t\tChoose from below options: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            audio_file= input("Enter path of cover Audio: ")
            # audio_file= "./resources/Audio_test.wav"
            audio_to_hide_path = input("Enter path of audio to be hidden: ")
            # audio_to_hide_path = "./resources/audio_file.wav"
            output_file = input("Enter the name stego file with extension: ")
            # output_file = "output_test999.wav"
            # gap_size = hide_audio_in_audio(audio_file, audio_to_hide_path, output_file,password) 
            hide_audio_in_audio(audio_file, audio_to_hide_path, output_file,password) 

        elif ch == 2:
            password = input("Enter password for decryption:")
            encoded_audio_file = input("Enter the path of the encoded audio file: ")
            # encoded_audio_file = "./output/encoded.wav"
            # encoded_audio_file = "output_test999.wav"
            decoded_audio_path = input("Enter the name of output audio file with extension to be generated: ")
            extract_audio_from_audio(encoded_audio_file, decoded_audio_path, password)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")

