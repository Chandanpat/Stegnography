import numpy as np
import pandas as pand
import os
import cv2
from matplotlib import pyplot as plt
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad



def encrypt(key, data):
    # print(type(data))
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    # print(ciphered_data)
    with open('./output/encrypted_iv.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphertext)
    return ciphertext


def key_generator(password):
    simple_key = get_random_bytes(16)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('./output/key_iv.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key


def decrypt(key, cypherText):
    with open('./output/encrypted_iv.bin', 'rb') as f:
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



def msgtobinary(msg):
    if type(msg) == str:
        result= ''.join([ format(ord(i), "08b") for i in msg ])
    
    elif type(msg) == bytes or type(msg) == np.ndarray:
        result= [ format(i, "08b") for i in msg ]
    
    elif type(msg) == int or type(msg) == np.uint8:
        result=format(msg, "08b")

    else:
        raise TypeError("Input type is not supported in this function")
    
    return result



def bytes_to_binary(byte_data):
    binary_data_list = []
    for byte in byte_data:
        binary_byte = bin(byte)[2:].zfill(8)  # Convert each byte to binary and pad with zeros to make it 8 bits
        binary_data_list.append(binary_byte)
    binary_data = ''.join(binary_data_list)
    return binary_data



def binary_to_bytes(binary_data):
    # Make sure the binary string length is a multiple of 8
    # if len(binary_data) % 8 != 0:
    #     raise ValueError("Binary data length must be a multiple of 8")

    # Remove any non-binary characters from the input string
    # binary_data = ''.join(filter(lambda x: x in '01', binary_data))

    # byte_data = bytearray()
    # for i in range(0, len(binary_data), 8):
    #     byte = int(binary_data[i:i + 8], 2)
    #     byte_data.append(byte)

    # return bytes(byte_data)
    byte_data = bytes(binary_data)
    return byte_data


def encrypt_image(key, image_path):
    img = cv2.imread(image_path)
    encrypted_data = encrypt(key, img.tobytes())
    return encrypted_data, img.shape

def decrypt_image(key, encrypted_data, image_shape):
    img_size = np.prod(image_shape)
    decrypted_data = decrypt(key, encrypted_data)[:img_size]
    img = np.frombuffer(decrypted_data, dtype=np.uint8).reshape(image_shape)
    return img

# def embed_image(frame, password):
#     # image_path = input("Enter path of image to be encrypted: ")
#     image_path = "./resources/image.jpg"
#     key = key_generator(password)
#     encrypted_image, image_shape = encrypt_image(key, image_path)

#     binary_data = bytes_to_binary(encrypted_image)
#     length_data = len(encrypted_image)

#     index_data = 0

#     for i in frame:
#         for pixel in i:
#             r, g, b = msgtobinary(pixel)
#             if index_data < length_data:
#                 pixel[0] = int(r[:-1] + binary_data[index_data], 2)
#                 index_data += 1
#             if index_data < length_data:
#                 pixel[1] = int(g[:-1] + binary_data[index_data], 2)
#                 index_data += 1
#             if index_data < length_data:
#                 pixel[2] = int(b[:-1] + binary_data[index_data], 2)
#                 index_data += 1
#             if index_data >= length_data:
#                 break
#     return frame, image_shape



# def extract_image(frame, key, image_shape):
#     data_binary = ""
#     decoded_data_list = []  # Use a list to accumulate decoded data efficiently
#     total_bytes = []

#     for i in frame:
#         for pixel in i:
#             r, g, b = msgtobinary(pixel)
#             data_binary += r[-1]
#             data_binary += g[-1]
#             data_binary += b[-1]

#             if len(data_binary) >= 8:
#                 # If we have accumulated at least 8 bits, convert to byte and store
#                 byte = int(data_binary[:8], 2)
#                 total_bytes.append(byte)
#                 data_binary = data_binary[8:]

#     if data_binary:
#         # If there are remaining bits, pad with zeros to form a byte and store
#         byte = int(data_binary.ljust(8, '0'), 2)
#         total_bytes.append(byte)

#     final_decoded_img = binary_to_bytes(total_bytes)
#     encrypted_image = decrypt_image(key, final_decoded_img, image_shape)
#     return encrypted_image




def embed_image(frame, password):
    image_path = "./resources/image_file3.png"  # Path to the image to be embedded
    key = key_generator(password)
    encrypted_image, image_shape = encrypt_image(key, image_path)

    binary_data = bytes_to_binary(encrypted_image)
    length_data = len(encrypted_image)

    index_data = 0
    for i in frame:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2)
                index_data += 1
            if index_data < length_data:
                pixel[1] = int(g[:-1] + binary_data[index_data], 2)
                index_data += 1
            if index_data < length_data:
                pixel[2] = int(b[:-1] + binary_data[index_data], 2)
                index_data += 1
            if index_data >= length_data:
                break
    return frame, image_shape

def extract_image(frame, key, image_shape):
    data_binary = ""
    decoded_data_list = []  # Use a list to accumulate decoded data efficiently
    total_bytes = []

    for i in frame:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            data_binary += r[-1]
            data_binary += g[-1]
            data_binary += b[-1]

            if len(data_binary) >= 8:
                # If we have accumulated at least 8 bits, convert to byte and store
                byte = int(data_binary[:8], 2)
                total_bytes.append(byte)
                data_binary = data_binary[8:]

    if data_binary:
        # If there are remaining bits, pad with zeros to form a byte and store
        byte = int(data_binary.ljust(8, '0'), 2)
        total_bytes.append(byte)

    # Convert the list of bytes to a bytes object
    final_decoded_img = bytes(total_bytes)
    
    # Decrypt the image and reshape it
    decrypted_image = decrypt_image(key, final_decoded_img, image_shape)
    
    return decrypted_image





def encode_vid_image(password):
    # cover_video = input("Enter path of cover video: ")
    cover_video = "./resources/cover_video.mp4"
    cap = cv2.VideoCapture(cover_video)
    vidcap = cv2.VideoCapture(cover_video)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    frame_width = int(vidcap.get(3))
    frame_height = int(vidcap.get(4))

    size = (frame_width, frame_height)
    # stego_video = input("Enter name of stego video with extension: ")
    # stego_video = "./output/" + stego_video
    stego_video = "./output/output1.mp4"
    out = cv2.VideoWriter(stego_video, fourcc, 25.0, size)
    max_frame = 0

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        max_frame += 1
    cap.release()
    print("Total number of Frame in selected Video:", max_frame)
    print("Enter the frame number where you want to embed data:")
    n = int(input())
    frame_number = 0

    while(vidcap.isOpened()):
        frame_number += 1
        ret, frame = vidcap.read()
        if ret == False:
            break
        if frame_number == n:
            frame, image_shape = embed_image(frame, password)
        out.write(frame)

    print("\nEncoded the data successfully in the video file.")
    return frame, image_shape




def decode_vid_image(frame, password, image_shape):
    with open('./output/key_iv.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    password1 = contents[0]
    key = contents[1]

    if str(password1, "utf-8") == password.strip():
        stego_video = input("Enter path of stego video: ")
        cap = cv2.VideoCapture(stego_video)
        max_frame = 0

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == False:
                break
            max_frame += 1
        print("Total number of Frame in selected Video:", max_frame)
        print("Enter the secret frame number from where you want to extract data:")
        n = int(input())
        vidcap = cv2.VideoCapture(stego_video)
        frame_number = 0

        while(vidcap.isOpened()):
            frame_number += 1
            ret, frame = vidcap.read()
            if ret == False:
                break
            if frame_number == n:
                extracted_image = extract_image(frame, key, image_shape)
                # cv2.imshow("Extracted Image", extracted_image)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()

                # Save the extracted image
                output_image_path = "./output/extracted_image.png"
                cv2.imwrite(output_image_path, extracted_image)
                print(f"Extracted image saved at: {output_image_path}")
                return
    else:
        print("Invalid Password!!")




def caller():
    while True:
        print("\n\t\tVIDEO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode an Image")  
        print("2. Decode an Image")  
        print("3. Exit")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1:
            password = input("Enter password for encryption: ")
            a,img_shape = encode_vid_image(password)
        elif choice1 == 2:
            password = input("Enter password for decryption: ")
            # decoded_image_path = "./output/decoded.jpg"
            # decode_vid_data(a,password).save(decoded_image_path)
            decode_vid_image(a, password, img_shape)
        elif choice1 == 3:
            break
        else:
            print("Incorrect Choice")
        print("\n")
