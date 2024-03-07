import cv2
import os
import shutil
import sys
from datetime import datetime
import tqdm
from PIL import Image
import numpy as np
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def encrypt(key, data):
    # print(type(data))
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    # print(ciphered_data)
    with open('./output/encrypted_vv.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphertext)
    return ciphertext


def key_generator(password):
    simple_key = get_random_bytes(32)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('./output/key_vv.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key


def decrypt(key, cypherText):
    with open('./output/encrypted_vv.bin', 'rb') as f:
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

def setupTempDir():
    os.makedirs("output/temp/", exist_ok=True)

def cleanupTempFiles():
    shutil.rmtree("output/temp/", ignore_errors=True)

def videoToImages(videoFile, type):
    valid_extensions = [".avi", ".mp4", ".mov", ".mkv"]  
    if any(videoFile.endswith(ext) for ext in valid_extensions):
        os.makedirs("output/temp/"+ type, exist_ok=True)
        vidcap = cv2.VideoCapture(videoFile)
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        success, image = vidcap.read()
        count = 0

        while success:
            countString = str(count).zfill(10)
            cv2.imwrite(f"output/temp/{type}/{type}{countString}.bmp", image)
            success, image = vidcap.read()
            count += 1
        return fps
    else:
        cleanupTempFiles()
        print("Incompatible video type. Supported formats: " + ", ".join(valid_extensions))

# def embedVideoLSB(secretFrame, coverFrame):
#     secret_image = Image.open(f"output/temp/secret/{secretFrame}")
#     cover_image = Image.open(f"output/temp/cover/{coverFrame}")

#     # Resize the secret video frame to match the dimensions of the cover video frame
#     secret_image = secret_image.resize(cover_image.size)

#     secret_data = np.array(secret_image)
#     cover_data = np.array(cover_image)

#     # Embed secret video data into LSB of cover video data
#     for i in range(3):  # Iterate over each channel (RGB)
#         cover_data[:, :, i] = (cover_data[:, :, i] & 0xFE) | ((secret_data[:, :, i] >> 7) & 1)

#     # Create the directory if it doesn't exist
#     os.makedirs("output/temp/encoded/", exist_ok=True)

#     merged_image = Image.fromarray(cover_data)
#     merged_image.save(f"output/temp/encoded/{coverFrame}")
        


def embedVideoLSB(secretFrame, coverFrame):
    image_to_hide = Image.open(f"output/temp/secret/{secretFrame}")
    image_to_hide_in = Image.open(f"output/temp/cover/{coverFrame}")
    width, height = image_to_hide.size
    width1,height1 = image_to_hide_in.size
    hide_image = image_to_hide.load()
    hide_in_image = image_to_hide_in.load()

    data = []

    n_bits = 1

    password = 'qwerty@1234567890'
    key = key_generator(password)
    # print(key)
    image_bytes = image_to_hide.tobytes()
    # print(image_bytes)
    encrypted_image = encrypt(key, image_bytes)

    # Use an iterator for the encrypted image bytes
    encrypted_iterator = iter(encrypted_image)


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
                # If there's no more data in the encrypted image, break the loop
                break
        
        for x in range(width,width1):
            # print(x)
            # print(y)
            r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]
            data.append((r_hide_in, g_hide_in, b_hide_in))


    for y in range(height,height1):
        for x in range(width1):
            # print(x)
            # print(y)
            r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]
            data.append((r_hide_in, g_hide_in, b_hide_in))


    #Create the directory if it doesn't exist
    os.makedirs("output/temp/encoded/", exist_ok=True)
    
    make_image(data, image_to_hide_in.size).save(f"output/temp/encoded/{coverFrame}")



# def embedVideoLSB(secretFrame, coverFrame):
#     image_to_hide = Image.open(f"output/temp/secret/{secretFrame}")
#     image_to_hide_in = Image.open(f"output/temp/cover/{coverFrame}")
#     width, height = image_to_hide.size
#     width1, height1 = image_to_hide_in.size
#     hide_image = image_to_hide.load()
#     hide_in_image = image_to_hide_in.load()

#     # print(width)
#     # print(height)
#     # print(width1)
#     # print(height1)

#     data = []

#     n_bits = 1

#     # a = 0
#     # b = 0

#     for y in range(height):
#         # b = 0
#         for x in range(width):
#             r_hide_pixel, g_hide_pixel, b_hide_pixel = hide_image[x, y]

#             # Remove the least n significant bits from the cover image
#             r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]
#             r_hide_in = remove_n_least_significant_bits(r_hide_in, n_bits)
#             g_hide_in = remove_n_least_significant_bits(g_hide_in, n_bits)
#             b_hide_in = remove_n_least_significant_bits(b_hide_in, n_bits)

#             data.append((r_hide_pixel + r_hide_in, g_hide_pixel + g_hide_in, b_hide_pixel + b_hide_in))

#             # b+=1

#             # print(b,end=" ")

#         for x in range(width,width1):
#             # print(x)
#             # print(y)
#             r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]
#             data.append((r_hide_in, g_hide_in, b_hide_in))
#         # print()
#         # print(b)
        
#     #     a+=1
#     # print(a)
#     # print(b)

#     for y in range(height,height1):
#         for x in range(width1):
#             # print(x)
#             # print(y)
#             r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]
#             data.append((r_hide_in, g_hide_in, b_hide_in))

#     # Create the directory if it doesn't exist
#     os.makedirs("output/temp/encoded/", exist_ok=True)

#     make_image(data, image_to_hide_in.size).save(f"output/temp/encoded/{coverFrame}")




def stegoEncodeFrames():
    secretFrames = sorted([img for img in os.listdir('output/temp/secret') if img.endswith(".bmp")])
    coverFrames = sorted([img for img in os.listdir('output/temp/cover') if img.endswith(".bmp")])

    # print(coverFrames)
    # print(secretFrames)

    print("Frame Encoding Progress:")
    for i in tqdm.tqdm(range(len(secretFrames))):

        secretFrame = secretFrames[i]
        coverFrame = coverFrames[i]
        embedVideoLSB(secretFrame, coverFrame)
        # print(coverFrames[i])
        # print(secretFrames[i])


def imagesToVideo(video_name, type, fps):
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    image_folder = f'output/temp/{type}'
    images = [img for img in os.listdir(image_folder) if img.endswith(".bmp")]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, _ = frame.shape
    video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))
    cv2.destroyAllWindows()
    video.release()

# def compareVideos(cover_video, encoded_video):
#     cover_cap = cv2.VideoCapture(cover_video)
#     encoded_cap = cv2.VideoCapture(encoded_video)

#     while True:
#         ret_cover, frame_cover = cover_cap.read()
#         ret_encoded, frame_encoded = encoded_cap.read()

#         if not ret_cover or not ret_encoded:
#             break

#         # Convert frames to grayscale for comparison
#         gray_cover = cv2.cvtColor(frame_cover, cv2.COLOR_BGR2GRAY)
#         gray_encoded = cv2.cvtColor(frame_encoded, cv2.COLOR_BGR2GRAY)

#         # Resize the images to have the same dimensions
#         height, width = min(gray_cover.shape[0], gray_encoded.shape[0]), min(gray_cover.shape[1], gray_encoded.shape[1])
#         gray_cover_resized = cv2.resize(gray_cover, (width, height))
#         gray_encoded_resized = cv2.resize(gray_encoded, (width, height))

#         # Compute absolute difference between resized frames
#         diff = cv2.absdiff(gray_cover_resized, gray_encoded_resized)

#         # Display the difference or save it to a file
#         cv2.imshow('Difference', diff)
#         cv2.waitKey(3000)  # Adjust as needed

#     cover_cap.release()
#     encoded_cap.release()
#     cv2.destroyAllWindows()



def extractFramesFromEncodedVideo(videoFile):
    os.makedirs("output/temp/extracted_frames/", exist_ok=True)
    vidcap = cv2.VideoCapture(videoFile)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    success, image = vidcap.read()
    count = 0

    while success:
        countString = str(count).zfill(10)
        cv2.imwrite(f"output/temp/extracted_frames/{countString}.bmp", image)  # Save frames as bmp
        success, image = vidcap.read()
        count += 1
    return fps


def stegoDecodeFrames():
    encodedFrames = sorted([img for img in os.listdir('output/temp/encoded') if img.endswith(".bmp")])

    # print(encodedFrames)

    print("Frame Decoding Progress:")
    secretFrame = "secret0000000000.bmp"
    for i in tqdm.tqdm(range(len(encodedFrames))):

        encodedFrame = encodedFrames[i]
        # print(encodedFrame)
        extractVideoLSB(encodedFrame,secretFrame)


def extractVideoLSB(encodedFrame,secretFrame):
    image_to_decode = Image.open(f"output/temp/encoded/{encodedFrame}")
    size_sample = Image.open(f"output/temp/secret/{secretFrame}")
    width, height = size_sample.size
    encoded_image = image_to_decode.load()

    data = []

    n_bits = 1

    password = 'qwerty@1234567890'

    for y in range(height):
        for x in range(width):
            r_encoded, g_encoded, b_encoded = encoded_image[x, y]

            r_encoded = get_n_least_significant_bits(r_encoded, n_bits)
            g_encoded = get_n_least_significant_bits(g_encoded, n_bits)
            b_encoded = get_n_least_significant_bits(b_encoded, n_bits)

            r_encoded = shit_n_bits_to_8(r_encoded, n_bits)
            g_encoded = shit_n_bits_to_8(g_encoded, n_bits)
            b_encoded = shit_n_bits_to_8(b_encoded, n_bits)

            data.append((r_encoded, g_encoded, b_encoded))

    decrypted_image = make_image(data, size_sample.size)

    with open('./output/key_vv.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    # print(contents)
    password1 = contents[0]
    key = contents[1]


    # Decrypt the image using the provided password
    with open('./output/key_vv.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    # print(contents)
    password1 = contents[0]
    key = contents[1]
    # print(key)
    # print(str(password1, "utf-8"), "\n", password.strip())
    if str(password1, "utf-8") == password.strip():
        decrypted_image_bytes = decrypted_image.tobytes()
        original_image_bytes = decrypt(key, decrypted_image_bytes)
        # print(original_image_bytes)
        #Create the directory if it doesn't exist
        os.makedirs("output/temp/decoded/", exist_ok=True)
        # Create a new image from the decrypted image bytes
        original_image = Image.frombytes("RGB", decrypted_image.size, original_image_bytes)
        original_image.save(f"output/temp/decoded/{encodedFrame}")
    else:
        print("Invalid Password!!")
        return 0
        
# def shift_n_bits_to_8(value, n):
#     # Shift the n least significant bits to the most significant position
#     return value << (8 - n)


# def extractVideoLSB(encodedFrame, secretFrame):
#     image_to_decode = Image.open(f"output/temp/encoded/{encodedFrame}")
#     size_sample = Image.open(f"output/temp/secret/{secretFrame}")
#     width, height = size_sample.size
#     encoded_image = image_to_decode.load()

#     data = []

#     n_bits = 1

#     password = 'qwerty@1234567890'

#     for y in range(height):
#         for x in range(width):
#             r_encoded, g_encoded, b_encoded = encoded_image[x, y]

#             r_encoded = get_n_least_significant_bits(r_encoded, n_bits)
#             g_encoded = get_n_least_significant_bits(g_encoded, n_bits)
#             b_encoded = get_n_least_significant_bits(b_encoded, n_bits)

#             r_encoded = shift_n_bits_to_8(r_encoded, n_bits)
#             g_encoded = shift_n_bits_to_8(g_encoded, n_bits)
#             b_encoded = shift_n_bits_to_8(b_encoded, n_bits)

#             data.append((r_encoded, g_encoded, b_encoded))

#     # Create the decoded image from the extracted data
#     decoded_image = make_image(data, size_sample.size)

#     # Save the decoded image
#     os.makedirs("output/temp/decoded/", exist_ok=True)
#     decoded_image.save(f"output/temp/decoded/{encodedFrame}")






# def extractSecretDataFromFrames():
#     extractedFrames = sorted([img for img in os.listdir('output/temp/extracted_frames/') if img.endswith(".bmp")])  # Look for bmp files

#     secret_data = []
#     for frame in extractedFrames:
#         frame_image = Image.open(f"output/temp/extracted_frames/{frame}")
#         frame_data = np.array(frame_image)

#         # Extract the LSBs from each channel to retrieve the secret data
#         secret_channel_0 = (frame_data[:, :, 0] & 1) << 7
#         secret_channel_1 = (frame_data[:, :, 1] & 1) << 7
#         secret_channel_2 = (frame_data[:, :, 2] & 1) << 7
        
#         # Combine the extracted LSBs from each channel
#         secret_data.extend([secret_channel_0, secret_channel_1, secret_channel_2])

#     return np.array(secret_data)


# def reconstructSecretVideo(secret_data, fps):
#     os.makedirs("output/extracted_secret_video/", exist_ok=True)
#     secret_frames = []
#     for i in range(0, len(secret_data), 3):
#         merged_data = np.zeros((secret_data[i].shape[0], secret_data[i].shape[1], 3), dtype=np.uint8)
#         merged_data[:, :, 0] = (merged_data[:, :, 0] & 0x7F) | (secret_data[i] << 7)  # Extracted from channel 0
#         merged_data[:, :, 1] = (merged_data[:, :, 1] & 0x7F) | (secret_data[i + 1] << 7)  # Extracted from channel 1
#         merged_data[:, :, 2] = (merged_data[:, :, 2] & 0x7F) | (secret_data[i + 2] << 7)  # Extracted from channel 2
#         secret_frames.append(merged_data)

#     for idx, frame_data in enumerate(secret_frames):
#         frame_image = Image.fromarray(frame_data)
#         frame_image.save(f"output/extracted_secret_video/frame_{idx}.bmp")

#     imagesToVideo("output/extracted_secret_video/extracted_secret_video.avi", "encoded", fps)



def caller():
    while True:
        print("\n\t\tVIDEO STEGANOGRAPHY OPERATIONS")
        print("1. Embed Secret Video in Cover Video")
        print("2. Extract Secret Video from Cover Video")
        print("3. Exit")
        choice1 = int(input("Enter the Choice: "))
        if choice1 == 1:
            setupTempDir()
            cover = 'resources/cover_test.avi'
            cover_fps = videoToImages(cover, "cover")
            secret = 'resources/secret_test.avi'
            videoToImages(secret, "secret")
            stegoEncodeFrames()
            output = 'output/output.avi'
            imagesToVideo(output, "encoded", cover_fps)
            print("\n\n\nVideo embeded successfully! Stego video saved as: ", output)
            # compareVideos('resources/cover_test.avi', 'output/output.avi')
            # cleanupTempFiles()
        elif choice1 == 2:
            encoded_video = 'output/output.avi'
            encoded_fps = extractFramesFromEncodedVideo(encoded_video)
            stegoDecodeFrames()
            imagesToVideo("output/extracted_secret_video.avi","decoded",encoded_fps)
            print("\n\n\nVideo extracted successfully! Output file saved as: output/extracted_secret_video.avi", )
            
            # cleanupTempFiles()
        elif choice1 == 3:
            break
        else:
            print("Incorrect Choice")
