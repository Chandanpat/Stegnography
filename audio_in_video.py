import os
import shutil
import cv2
from PIL import Image
from moviepy.editor import *
from pydub import AudioSegment
import wave
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import numpy as np



def encrypt(key, data):
    # print(type(data))
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    # print(ciphered_data)
    with open('./output/encrypted_av.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphertext)
    return ciphertext



def key_generator(password):
    simple_key = get_random_bytes(32)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('./output/key_av.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key



def decrypt(key, cypherText):
    with open('./output/encrypted_av.bin', 'rb') as f:
        iv = f.read(16)
        cypherText = f.read()
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        og = unpad(cipher.decrypt(cypherText), AES.block_size)
    return og



def hide_audio_in_audio(cover_audio, secret_audio, output_file, password):
    print(type(cover_audio))
    print(type(secret_audio))
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
    os.remove(cover_audio)



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
    with open('./output/key_av.bin', 'rb') as f:
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
            output_audio_file.setframerate(44100)
            output_audio_file.writeframes(decrypted_audio_bytes)

        os.remove(encoded_audio_file)
    else:
        print("Invalid Password!!")    



# def get_audio1(base_filename, video_object):       # function that stores the audio in variable
#     """Returns the audio data only of a video clip"""
#     audio_temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
#     audio_temp_file.close()  # Close the file so that it can be reopened for writing
#     audio_filename = audio_temp_file.name
    
#     try:
#         video_object.audio.write_audiofile(audio_filename, codec='pcm_s16le')  # Writing audio data to a temporary file
#         with open(audio_filename, 'rb') as f:
#             audio_data = f.read()  # Read the audio data from the temporary file
#     finally:
#         os.unlink(audio_filename)  # Delete the temporary file

#     return audio_data

# def get_audio(base_filename, video_object):
#     """Returns the audio track only of a video clip"""
#     video_object.audio.write_audiofile(filename=f'output\\{base_filename}_audio.wav')
def normalize_audio(audio_path):
    audio = AudioSegment.from_file(audio_path)
    normalized_audio = audio.normalize()
    return normalized_audio



def get_audio(base_filename, video_object):
    """Returns the audio track only of a video clip"""
    audio_path = f'output\\{base_filename}_audio.wav'
    video_object.audio.write_audiofile(filename=audio_path)
    normalized_audio = normalize_audio(audio_path)
    normalized_audio.export(audio_path, format='wav')  # Overwrite the audio file with the normalized version



def get_frames(video_object, base_filename):
    """Returns the directory path where frames are saved"""
    directory = "output\\" + base_filename + '_frames\\'
    if not os.path.isdir(directory): 
        os.makedirs(directory)
    for index, frame in enumerate(video_object.iter_frames()):
        img = Image.fromarray(frame, 'RGB')
        img.save(f'{directory}{index}.png')
    return directory    



def combine_audio_video(frames_directory, audio_path, og_path, output):
    """Combines an audio and a video object together"""
    capture = cv2.VideoCapture(og_path)  # Stores OG Video into a Capture Window
    fps = capture.get(cv2.CAP_PROP_FPS)  # Extracts FPS of OG Video

    video_path_real = frames_directory + "\\%d.png"  # To Get All Frames in Folder

    os.system(
        f"ffmpeg -framerate {int(fps)} -i \"{video_path_real}\" -codec copy output\\combined_video_only.mkv")  # Combining the Frames into a Video
    os.system(
        f"ffmpeg -i output\\combined_video_only.mkv -i \"{audio_path}\" -codec copy \"{output}\"")  # Combining the Frames and Audio into a Video
    
    # os.remove(frames_directory)
    shutil.rmtree(frames_directory, ignore_errors=True)
    os.remove(audio_path)
    os.remove("./output/combined_video_only.mkv")             



def hide_audio_in_video(og_video, og_audio, password, output_video):
    base_filename = os.path.splitext(os.path.basename(og_video))[0]
    video_object = VideoFileClip(og_video)

    # frames-folder extracted from Video
    frames_directory = get_frames(video_object, base_filename)

    # cover-audio extracted from Video
    # cover_audio = get_audio(base_filename, video_object)        # Use this audio as cover_Audio
    get_audio(base_filename, video_object)        # Use this audio as cover_Audio
    cover_audio = f'output\\{base_filename}_audio.wav'

    # Use Audio_In_Audio Hiding
    output_file = "./output/output_test999.wav"         # Assigning name for encoded_audio after hide_audio_in_audio
    # encoded_audio_data = hide_audio_in_audio(cover_audio, og_audio, password) 
    hide_audio_in_audio(cover_audio, og_audio, output_file, password) 

    # Combine audio and video
    encoded_audio_data = "./output/output_test999.wav"  # storing the encoded_audio in variable for combine_audio_video fun
    output = "./output/"+output_video
    combine_audio_video(frames_directory, encoded_audio_data, og_video, output)
    print("\n\n\nAudio embeded successfully! Stego video saved as: ", output)


    
def unhide_audio_from_encryptedVideo(encrypted_video, password, output_audio):
    base_filename = os.path.splitext(os.path.basename(encrypted_video))[0]
    video_object = VideoFileClip(encrypted_video)

    # cover-audio extracted from Video
    get_audio(base_filename, video_object)
    extracted_audio = f'output\\{base_filename}_audio.wav'

    # Use Audio_In_Audio Unhiding
    decoded_audio_path = "./output/"+output_audio
    extract_audio_from_audio(extracted_audio, decoded_audio_path, password)

    print("\n\n\nAudio extracted successfully! Output file saved as: ",decoded_audio_path)

    #return extracted audio



def main():
    while True:
        print("\n\t\tAUDIO IN VIDEO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Audio in video")  
        print("2. Decode Audio from Video")  
        print("3. Exit")  
        option = int(input("Enter the Choice: "))

        if option == 1:
            og_video = input("Enter original video file path: ")
            og_audio = input("Enter original audio file path: ")
            output_video = input("Enter the name of stego file to be generated: ")
            password = input("Enter password for encryption: ")
            hide_audio_in_video(og_video, og_audio, password, output_video)

        elif option == 2:
            password = input("Enter password for encryption: ")
            encrypted_video = input("Enter encrypted video file path: ")
            output_audio = input("Enter the name of output audio file to be generated: ")
            unhide_audio_from_encryptedVideo(encrypted_video, password, output_audio)

        else:
            print("Incorrect Choice!!")

if __name__ == "__main__":
    main()
