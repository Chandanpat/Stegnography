import os
import shutil
import cv2
from PIL import Image
from moviepy.editor import *
from pydub import AudioSegment
import wave
from essentials import *
from calculations import *


def hide_audio_in_audio(cover_audio, secret_audio, output_file, password):
    # Open the cover audio file for reading
    with wave.open(cover_audio, 'rb') as cover_audio_file:
        cover_frames = cover_audio_file.readframes(-1)

    # Open the secret audio file for reading
    with wave.open(secret_audio, 'rb') as secret_audio_file:
        secret_frames = secret_audio_file.readframes(-1)

    # Encrypt the secret audio data
    key = key_generator(password,"av")
    encrypted_audio = encrypt(key, secret_frames, "av")

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



def extract_audio_from_audio(encoded_audio_file, decoded_audio_path, password, key):
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

    # Decrypt the encrypted audio
    decrypted_audio_bytes = decrypt(key, encrypted_audio, "av")

    # Write the decrypted audio to the output file
    with wave.open(decoded_audio_path, 'wb') as output_audio_file:
        output_audio_file.setparams(audio_file.getparams())
        output_audio_file.setframerate(44100)
        output_audio_file.writeframes(decrypted_audio_bytes)
    os.remove(encoded_audio_file)    



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



def hide_audio_in_video(password):
    og_video = input("Enter path of cover video: ")
    og_audio = input("Enter path of audio file to be hidden: ")
    output_video = input("Enter the name of Stego file to be generated: ")
    base_filename = os.path.splitext(os.path.basename(og_video))[0]
    video_object = VideoFileClip(og_video)

    # frames-folder extracted from Video
    frames_directory = get_frames(video_object, base_filename)

    get_audio(base_filename, video_object)        # Use this audio as cover_Audio
    cover_audio = f'output\\{base_filename}_audio.wav'
    print("Payload = ",calculate_payload_video_audio(cover_audio))

    # Use Audio_In_Audio Hiding
    output_file = "./output/output_test999.wav"         # Assigning name for encoded_audio after hide_audio_in_audio

    hide_audio_in_audio(cover_audio, og_audio, output_file, password) 

    # Combine audio and video
    encoded_audio_data = "./output/output_test999.wav"  # storing the encoded_audio in variable for combine_audio_video fun
    output = "./output/"+output_video
    combine_audio_video(frames_directory, encoded_audio_data, og_video, output)
    print("\n\n\nAudio embeded successfully! Stego video saved as: ", output)
    return og_audio


    
def unhide_audio_from_encryptedVideo(password):
    key,check = checkPass(password,'av')
    if check == True:
        encrypted_video = input("Enter encrypted video file path: ")
        output_audio = input("Enter the name of output audio file to be generated: ")
        base_filename = os.path.splitext(os.path.basename(encrypted_video))[0]
        video_object = VideoFileClip(encrypted_video)

        # cover-audio extracted from Video
        get_audio(base_filename, video_object)
        extracted_audio = f'output\\{base_filename}_audio.wav'

        # Use Audio_In_Audio Unhiding
        decoded_audio_path = "./output/"+output_audio
        extract_audio_from_audio(extracted_audio, decoded_audio_path, password, key)

        print("\n\n\nAudio extracted successfully! Output file saved as: ",decoded_audio_path)
        return decoded_audio_path
    
    else:
        print("Invalid Password!!")



def caller():
    while True:
        print("\n\t\tAUDIO IN VIDEO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Audio in video")  
        print("2. Decode Audio from Video")  
        print("3. Exit")  
        option = int(input("Enter the Choice: "))

        if option == 1:
            password = input("Enter password for encryption: ")
            inp = hide_audio_in_video(password)

        elif option == 2:
            password = input("Enter password for decryption: ")
            out = unhide_audio_from_encryptedVideo(password)
            print("MSE = ",calculate_mse_av(inp,out))

        elif option == 3:
            print("\n\nExiting.....")
            break

        else:
            print("Incorrect Choice!!")
