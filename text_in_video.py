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



def encrypt(key, msg):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphered_data = cipher.encrypt(pad(msg, AES.block_size))
    # print(ciphered_data)
    with open('./output/encrypted.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphered_data)
    return ciphered_data


def key_generator(password):
    simple_key = get_random_bytes(32)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('./output/key.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key


def decrypt(key, cypherText):
    with open('./output/encrypted.bin', 'rb') as f:
        iv = f.read(16)
        cypherText = f.read()
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        og = unpad(cipher.decrypt(cypherText), AES.block_size)
    return og



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
    binary_data = ""
    for byte in byte_data:
        binary_byte = bin(byte)[2:].zfill(8)  # Convert each byte to binary and pad with zeros to make it 8 bits
        binary_data += binary_byte
    return binary_data



def binary_to_bytes(binary_data):
    # Make sure the binary string length is a multiple of 8
    # if len(binary_data) % 8 != 0:
    #     raise ValueError("Binary data length must be a multiple of 8")

    # Remove any non-binary characters from the input string
    binary_data = ''.join(filter(lambda x: x in '01', binary_data))

    byte_data = bytearray()
    for i in range(0, len(binary_data), 8):
        byte = int(binary_data[i:i + 8], 2)
        byte_data.append(byte)

    return bytes(byte_data)



def embed(frame,password):
    msg = bytes(input("Enter message to be encrypted: "), "utf-8")
    key = key_generator(password)
    # print(key)
    encrypted_message = encrypt(key, msg)
    print("The encrypted data is : ",encrypted_message)
    if (len(encrypted_message) == 0): 
        raise ValueError('Data entered to be encoded is empty')

    # encrypted_message +='*^*^*'
    
    binary_data = bytes_to_binary(encrypted_message)
    length_data = len(encrypted_message)
    
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
        return frame
    


def extract(frame,key):
    data_binary = ""
    final_decoded_msg = ""
    for i in frame:
        for pixel in i:
            r, g, b = msgtobinary(pixel) 
            data_binary += r[-1]  
            data_binary += g[-1]  
            data_binary += b[-1]  
            total_bytes = [ data_binary[i: i+8] for i in range(0, len(data_binary), 8) ]
            decoded_data = ""
            for byte in total_bytes:
                decoded_data += chr(int(byte, 2))
                # if decoded_data[-5:] == "*^*^*": 
                for i in range(0,len(decoded_data)):
                    final_decoded_msg += decoded_data[i]
                final_decoded_msg = binary_to_bytes(final_decoded_msg)
                original_msg = decrypt(key,final_decoded_msg)
                print("\n\nThe Encoded data which was hidden in the Video was :--\n",original_msg.decode('utf-8'))
                return



def encode_vid_data(password):
    cover_video = input("Enter path of cover video: ")
    cap=cv2.VideoCapture(cover_video)
    vidcap = cv2.VideoCapture(cover_video)    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    frame_width = int(vidcap.get(3))
    frame_height = int(vidcap.get(4))

    size = (frame_width, frame_height)
    stego_video = input("Enter name of stego video with extension: ")
    stego_video = "./output/" + stego_video
    out = cv2.VideoWriter(stego_video,fourcc, 25.0, size)
    max_frame=0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        max_frame+=1
    cap.release()
    print("Total number of Frame in selected Video :",max_frame)
    print("Enter the frame number where you want to embed data : ")
    n=int(input())
    frame_number = 0
    while(vidcap.isOpened()):
        frame_number += 1
        ret, frame = vidcap.read()
        if ret == False:
            break
        if frame_number == n:    
            change_frame_with = embed(frame,password)
            frame_ = change_frame_with
            frame = change_frame_with
        out.write(frame)
    
    print("\nEncoded the data successfully in the video file.")
    return frame_



def decode_vid_data(frame_,password):
    with open('./output/key.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    # print(contents)
    password1 = contents[0]
    key = contents[1]
    # print(key)
    # print(str(password1, "utf-8"), "\n", password.strip())
    if str(password1, "utf-8") == password.strip():
        stego_video = input("Enter path of stego video: ")
        cap = cv2.VideoCapture(stego_video)
        max_frame=0
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == False:
                break
            max_frame+=1
        print("Total number of Frame in selected Video :",max_frame)
        print("Enter the secret frame number from where you want to extract data")
        n=int(input())
        vidcap = cv2.VideoCapture(stego_video)
        frame_number = 0
        while(vidcap.isOpened()):
            frame_number += 1
            ret, frame = vidcap.read()
            if ret == False:
                break
            if frame_number == n:
                extract(frame_,key)
                return
    else:
        print("Invalid Password!!")
    


def caller():
    while True:
        print("\n\t\tVIDEO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode the Text message")  
        print("2. Decode the Text message")  
        print("3. Exit")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1:
            password = input("Enter password for encryption: ")
            a=encode_vid_data(password)
        elif choice1 == 2:
            password = input("Enter password for decryption: ")
            decode_vid_data(a,password)
        elif choice1 == 3:
            break
        else:
            print("Incorrect Choice")
        print("\n")