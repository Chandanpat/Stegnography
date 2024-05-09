from PIL import Image
import soundfile as sf
import numpy as np
import cv2
def calculate_required_percentage_ii(cover_image_size, secret_image_size):
    # Calculate the total number of pixels in the cover image
    total_cover_pixels = cover_image_size[0] * cover_image_size[1]
    
    # Calculate the total number of pixels in the secret image
    total_secret_pixels = secret_image_size[0] * secret_image_size[1]
    
    # Calculate the required percentage
    required_percentage = (total_secret_pixels / total_cover_pixels) * 100
    
    return required_percentage


# def calculate_payload_capacity_percentage_ti(image_path,msg):
#     # Open the cover image
#     image = Image.open(image_path)
#     width, height = image.size
#     color_depth = image.mode  # This will return the color mode of the image, e.g., 'RGB'
#     # Calculate the total number of pixels
#     total_pixels = width * height
#     # Determine the number of bits per pixel based on color depth
#     if color_depth == 'RGB':  # Assuming 24-bit color depth (8 bits per channel)
#         bits_per_pixel = 24
#     else:
#         # Handle other color modes if necessary
#         pass
#     # Calculate the total number of bits available for data hiding
#     total_bits = total_pixels * bits_per_pixel
#     # Assuming you know the size of the encrypted message (in bits)
#     encrypted_message_size_bits = len(msg)*8  # Replace ... with the size of your encrypted message in bits
#     # Calculate the payload capacity percentage
#     payload_capacity_percentage = (encrypted_message_size_bits / total_bits) * 100
#     return payload_capacity_percentage

def calculate_payload_capacity(path):
    image = Image.open(path)
    width, height = image.size
    total_pixels = width * height
    bits_per_pixel = 3  # You're modifying 1 bit per color component (RGB)
    total_capacity_bits = total_pixels * bits_per_pixel
    # Assuming ASCII encoding, each character requires 8 bits
    total_capacity_characters = total_capacity_bits // 8
    return total_capacity_characters

def calculate_mse(input_text, output_text):
    # Convert input and output texts to ASCII arrays
    # Convert input and output texts to ASCII arrays
    input_ascii = [ord(char) for char in input_text]
    output_ascii = [ord(char) for char in output_text]

    # Ensure both arrays have the same length
    max_length = max(len(input_ascii), len(output_ascii))
    input_ascii += [0] * (max_length - len(input_ascii))
    output_ascii += [0] * (max_length - len(output_ascii))

    # Compute squared differences and sum them
    squared_diff_sum = sum((input_char - output_char) ** 2 for input_char, output_char in zip(input_ascii, output_ascii))

    # Calculate MSE
    mse = squared_diff_sum / max_length
    return mse



def calculate_mse_ii(input_image_path, output_image_path):
    input_image = Image.open(input_image_path)
    output_image = Image.open(output_image_path)

    # Ensure the images have the same size
    if input_image.size != output_image.size:
        raise ValueError("Input and output images must have the same dimensions.")

    # Load pixel data
    input_pixels = input_image.load()
    output_pixels = output_image.load()

    width, height = input_image.size
    num_pixels = width * height

    # Calculate MSE
    squared_diff_sum = 0
    for y in range(height):
        for x in range(width):
            input_r, input_g, input_b = input_pixels[x, y]
            output_r, output_g, output_b = output_pixels[x, y]
            squared_diff_sum += (input_r - output_r) ** 2 + (input_g - output_g) ** 2 + (input_b - output_b) ** 2

    mse = squared_diff_sum / num_pixels

    # Normalize the MSE
    max_intensity_value = 255  # Maximum pixel intensity value
    normalized_mse = mse / (max_intensity_value ** 2)
    return normalized_mse



import soundfile as sf
def calculate_psnr(mse, max_value=1):
    # Calculate PSNR
    psnr = 10 * np.log10((max_value ** 2) / mse)
    return psnr

def calculate_mse_av(input_audio_path, decoded_audio_path):
    # Load input and decoded audio files
    input_audio, sr_input = sf.read(input_audio_path)
    decoded_audio, sr_decoded = sf.read(decoded_audio_path)

    # Convert stereo audio to mono by averaging channels
    if len(input_audio.shape) > 1:
        input_audio = np.mean(input_audio, axis=1)
    if len(decoded_audio.shape) > 1:
        decoded_audio = np.mean(decoded_audio, axis=1)

    # Ensure both audio files have the same length
    min_length = min(len(input_audio), len(decoded_audio))
    input_audio = input_audio[:min_length]
    decoded_audio = decoded_audio[:min_length]

    # Calculate Mean Squared Error (MSE)
    mse = np.mean((input_audio - decoded_audio) ** 2)
    return mse


import wave

def calculate_payload_video_audio(audio_file):
    # Open the audio file for reading
    with wave.open(audio_file, 'rb') as audio:
        # Get the number of frames in the audio file
        total_frames = audio.getnframes()
        # Get the number of channels (e.g., mono or stereo)
        num_channels = audio.getnchannels()
        # Get the sample width (in bytes) - determines the bit depth
        sample_width = audio.getsampwidth()

        # Calculate the maximum payload based on the audio properties
        max_payload_bytes = total_frames * num_channels * sample_width

        return max_payload_bytes
    


def calculate_payload_video_frames(video_path, frame_number):
    cap = cv2.VideoCapture(video_path)
    frame_number = int(frame_number)

    if not cap.isOpened():
        print("Error: Unable to open video file")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_number <= 0 or frame_number > frame_count:
        print("Error: Invalid frame number")
        return

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame")
        return

    # Calculate maximum payload size
    height, width, _ = frame.shape
    max_payload_size = height * width * 3  # Assuming each pixel has 3 color channels (R, G, B)

    print("Maximum payload size of frame {} in the given video: {} bits".format(frame_number, max_payload_size))

    cap.release()








