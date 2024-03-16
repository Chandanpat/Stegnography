import wave
from essentials import *



def hide_audio_in_audio(password):
    cover_audio= input("Enter path of cover Audio: ")
    # audio_file= "./resources/Audio_test.wav"
    secret_audio = input("Enter path of audio to be hidden: ")
    # audio_to_hide_path = "./resources/audio_file.wav"
    output_file = "./output/"+input("Enter the name stego file with extension to be generated: ")
    # output_file = "output_test999.wav"
    # Open the cover audio file for reading
    with wave.open(cover_audio, 'rb') as cover_audio_file:
        cover_frames = cover_audio_file.readframes(-1)

    # Open the secret audio file for reading
    with wave.open(secret_audio, 'rb') as secret_audio_file:
        secret_frames = secret_audio_file.readframes(-1)

    # Encrypt the secret audio data
    key = key_generator(password,'aa')
    encrypted_audio = encrypt(key, secret_frames,'aa')

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

    print("\n\n\nAudio embedded successfully! Output file saved as:", output_file)

    

def extract_audio_from_audio(password):
    key,check = checkPass(password,'aa')
    if check == True:
        encoded_audio_file = input("Enter the path of the encoded audio file: ")
        # encoded_audio_file = "./output/encoded.wav"
        # encoded_audio_file = "output_test999.wav"
        decoded_audio_path = "./output/"+input("Enter the name of output file with extension to be generated: ")
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

        decrypted_audio_bytes = decrypt(key, encrypted_audio,"aa")

        # Write the decrypted audio to the output file
        with wave.open(decoded_audio_path, 'wb') as output_audio_file:
            output_audio_file.setparams(audio_file.getparams())
            output_audio_file.setframerate(22050)
            output_audio_file.writeframes(decrypted_audio_bytes)

        print("\n\n\nAudio extracted successfully! Output file saved as: ", decoded_audio_path)
    else:
        print("Invalid Password!!")



def caller():
    while True:
        print("\n\t\tAUDIO IN AUDIO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Audio in Audio")  
        print("2. Decode Audio from Audio")  
        print("3. Exit")
        ch = int(input("\n\t\tChoose from below options: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            hide_audio_in_audio(password) 

        elif ch == 2:
            password = input("Enter password for decryption: ")
            extract_audio_from_audio(password)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")

