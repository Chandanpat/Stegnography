import numpy as np
import cv2
from essentials import *



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
    binary_data = ''.join(filter(lambda x: x in '01', binary_data))

    byte_data = bytearray()
    for i in range(0, len(binary_data), 8):
        byte = int(binary_data[i:i + 8], 2)
        byte_data.append(byte)

    return bytes(byte_data)



def embed(frame,password):
    msg = bytes(input("Enter the text message to hide: "), "utf-8")
    key = key_generator(password,"tv")
    encrypted_message = encrypt(key, msg, "tv")
    if (len(encrypted_message) == 0): 
        raise ValueError('Data entered to be encoded is empty')
    
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
                for i in range(0,len(decoded_data)):
                    final_decoded_msg += decoded_data[i]
                final_decoded_msg = binary_to_bytes(final_decoded_msg)
                original_msg = decrypt(key,final_decoded_msg,"tv")
                print("\n\n\nMessage decoded from the stego file:- ",original_msg.decode('utf-8'))
                return



def encode_vid_data(password):
    cover_video = input("Enter path of cover video: ")
    cap=cv2.VideoCapture(cover_video)
    vidcap = cv2.VideoCapture(cover_video)    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    frame_width = int(vidcap.get(3))
    frame_height = int(vidcap.get(4))
    size = (frame_width, frame_height)
    stego_video = input("Enter name of Stego video with extension to be generated: ")
    stego_video = "./output/" + stego_video
    out = cv2.VideoWriter(stego_video,fourcc, 25.0, size)
    max_frame=0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        max_frame+=1
    cap.release()
    print("Total number of Frame in selected Video: ",max_frame)
    n=int(input("Enter the frame number where you want to embed data: "))
    frame_number = 0
    while(vidcap.isOpened()):
        frame_number += 1
        ret, frame = vidcap.read()
        if ret == False:
            break
        if frame_number == n:    
            change_frame_with = embed(frame,password)
            frame = change_frame_with
        out.write(frame)
    
    print("\n\n\nText embedded successfully! Stego file saved as: ", stego_video)



def decode_vid_data(password):
    key,check = checkPass(password,'tv')
    if check == True:
        stego_video = input("Enter path of stego video: ")
        cap = cv2.VideoCapture(stego_video)
        max_frame=0
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == False:
                break
            max_frame+=1
        print("Total number of Frame in selected Video: ",max_frame)
        n=int(input("Enter the secret frame number from where you want to extract data: "))
        vidcap = cv2.VideoCapture(stego_video)
        frame_number = 0
        while(vidcap.isOpened()):
            frame_number += 1
            ret, frame = vidcap.read()
            if ret == False:
                break
            if frame_number == n:
                extract(frame,key)
                return
    else:
        print("Invalid Password!!")
    


def caller():
    while True:
        print("\n\t\tTEXT IN VIDEO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Text in Video")  
        print("2. Decode Text from Video")  
        print("3. Exit")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1:
            password = input("Enter password for encryption: ")
            encode_vid_data(password)
        elif choice1 == 2:
            password = input("Enter password for decryption: ")
            decode_vid_data(password)
        elif choice1 == 3:
            print("Exiting.....")
            break
        else:
            print("Incorrect Choice")
        print("\n")



# import random
# import numpy as np
# import cv2
# from essentials import *

# # Function to convert message to binary
# def msgtobinary(msg):
#     if type(msg) == str:
#         result = ''.join([format(ord(i), "08b") for i in msg])
#     elif type(msg) == bytes or type(msg) == np.ndarray:
#         result = [format(i, "08b") for i in msg]
#     elif type(msg) == int or type(msg) == np.uint8:
#         result = format(msg, "08b")
#     else:
#         raise TypeError("Input type is not supported in this function")
#     return result

# # Function to convert bytes to binary
# def bytes_to_binary(byte_data):
#     binary_data = ""
#     for byte in byte_data:
#         binary_byte = bin(byte)[2:].zfill(8)  # Convert each byte to binary and pad with zeros to make it 8 bits
#         binary_data += binary_byte
#     return binary_data

# # Function to convert binary to bytes
# def binary_to_bytes(binary_data):
#     binary_data = ''.join(filter(lambda x: x in '01', binary_data))

#     byte_data = bytearray()
#     for i in range(0, len(binary_data), 8):
#         byte = int(binary_data[i:i + 8], 2)
#         byte_data.append(byte)

#     return bytes(byte_data)

# # Function to generate a unique identifier or watermark
# def generate_watermark(length=10):
#     watermark = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=length))
#     return watermark

# # Modify the embed function to include embedding of watermark
# def embed(frame, password):
#     # Embed watermark
#     watermark = generate_watermark()
#     watermark_binary = msgtobinary(watermark)
#     binary_data = watermark_binary

#     # Embed text message
#     msg = bytes(input("Enter the text message to hide: "), "utf-8")
#     key = key_generator(password, "tv")
#     encrypted_message = encrypt(key, msg, "tv")
#     if len(encrypted_message) == 0:
#         raise ValueError('Data entered to be encoded is empty')

#     binary_data += bytes_to_binary(encrypted_message)
#     length_data = len(encrypted_message) + len(watermark)
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
#     return frame, watermark

# # Modify the extract function to identify frames containing watermark
# def extract(frame, key):
#     data_binary = ""
#     watermark_length = 10  # Assuming a watermark length of 10 characters
#     watermark_found = False

#     for i in frame:
#         for pixel in i:
#             r, g, b = msgtobinary(pixel)
#             data_binary += r[-1]
#             data_binary += g[-1]
#             data_binary += b[-1]
#             total_bytes = [data_binary[i: i + 8] for i in range(0, len(data_binary), 8)]
#             decoded_data = ""

#             for byte in total_bytes:
#                 decoded_data += chr(int(byte, 2))

#                 # Check if watermark is found
#                 if len(decoded_data) >= watermark_length:
#                     if decoded_data[-watermark_length:] == generate_watermark():
#                         watermark_found = True
#                         decoded_data = decoded_data[:-watermark_length]
#                         break

#             if watermark_found:
#                 # Extract the rest of the message
#                 final_decoded_msg = binary_to_bytes(decoded_data)
#                 original_msg = decrypt(key, final_decoded_msg, "tv")
#                 print("\n\n\nMessage decoded from the stego file:- ", original_msg.decode('utf-8'))
#                 return
#             else:
#                 print("\n\n\nData entered to be encoded is empty!!")
#                 return

# # Function to encode video data
# def encode_vid_data(password):
#     cover_video = input("Enter path of cover video: ")
#     cap = cv2.VideoCapture(cover_video)
#     vidcap = cv2.VideoCapture(cover_video)
#     fourcc = cv2.VideoWriter_fourcc(*'XVID')
#     frame_width = int(vidcap.get(3))
#     frame_height = int(vidcap.get(4))
#     size = (frame_width, frame_height)
#     stego_video = input("Enter name of Stego video with extension to be generated: ")
#     stego_video = "./output/" + stego_video
#     out = cv2.VideoWriter(stego_video, fourcc, 25.0, size)
#     max_frame = 0
#     while(cap.isOpened()):
#         ret, frame = cap.read()
#         if ret == False:
#             break
#         max_frame += 1
#     cap.release()
#     print("Total number of Frame in selected Video: ", max_frame)
#     n = int(input("Enter the frame number where you want to embed data: "))
#     frame_number = 0
#     while(vidcap.isOpened()):
#         frame_number += 1
#         ret, frame = vidcap.read()
#         if ret == False:
#             break
#         if frame_number == n:
#             frame, watermark = embed(frame, password)
#         out.write(frame)
#     print("\n\n\nText embedded successfully! Stego file saved as: ", stego_video)

# # Function to decode video data
# def decode_vid_data(password):
#     key, check = checkPass(password, 'tv')
#     if check == True:
#         stego_video = input("Enter path of stego video: ")
#         cap = cv2.VideoCapture(stego_video)
#         max_frame = 0
#         while(cap.isOpened()):
#             ret, frame = cap.read()
#             if ret == False:
#                 break
#             max_frame += 1
#         print("Total number of Frame in selected Video: ", max_frame)
#         n = int(input("Enter the secret frame number from where you want to extract data: "))
#         vidcap = cv2.VideoCapture(stego_video)
#         frame_number = 0
#         while(vidcap.isOpened()):
#             frame_number += 1
#             ret, frame = vidcap.read()
#             if ret == False:
#                 break
#             if frame_number == n:
#                 extract(frame, key)
#                 return
#     else:
#         print("Invalid Password!!")

# # Function to handle user choices
# def caller():
#     while True:
#         print("\n\t\tTEXT IN VIDEO STEGANOGRAPHY OPERATIONS")
#         print("1. Encode Text in Video")
#         print("2. Decode Text from Video")
#         print("3. Exit")
#         choice1 = int(input("Enter the Choice: "))
#         if choice1 == 1:
#             password = input("Enter password for encryption: ")
#             encode_vid_data(password)
#         elif choice1 == 2:
#             password = input("Enter password for decryption: ")
#             decode_vid_data(password)
#         elif choice1 == 3:
#             print("Exiting.....")
#             break
#         else:
#             print("Incorrect Choice")
#         print("\n")
