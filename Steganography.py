from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import numpy as np
import wave
import os
import cv2
import shutil
from moviepy.editor import *
from pydub import AudioSegment





# essential functions
def encrypt(key, msg, type):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphered_data = cipher.encrypt(pad(msg, AES.block_size))
    with open('./output/encrypted_'+type+'.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphered_data)
    return ciphered_data



def key_generator(password,type):
    simple_key = get_random_bytes(32)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('./output/key_'+type+'.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key



def decrypt(key, cypherText, type):
    with open('./output/encrypted_'+type+'.bin', 'rb') as f:
        iv = f.read(16)
        cypherText = f.read()
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        og = unpad(cipher.decrypt(cypherText), AES.block_size)
        return og
            


def checkPass(password,type):
    with open('./output/key_'+type+'.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    # print(contents)
    password1 = contents[0]
    key = contents[1]
    # print(key)
    # print(str(password1, "utf-8"), "\n", password.strip())
    if str(password1, "utf-8") == password.strip():
        return key,True
    else:
        return '',



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
        binary_byte = bin(byte)[2:].zfill(8) 
        binary_data_list.append(binary_byte)
    binary_data = ''.join(binary_data_list)
    return binary_data



def binary_to_bytes(binary_data):
    byte_data = bytes(binary_data)
    return byte_data



def encrypt_image(key, image_path):
    img = cv2.imread(image_path)
    encrypted_data = encrypt(key, img.tobytes(), "iv")
    return encrypted_data, img.shape



def decrypt_image(key, encrypted_data, image_shape):
    img_size = np.prod(image_shape)
    decrypted_data = decrypt(key, encrypted_data, "iv")[:img_size]
    try:
        img = np.frombuffer(decrypted_data, dtype=np.uint8).reshape(image_shape)
        return img
    except Exception as Error:
        print(type(Error).__name__)



def bytes_to_binary2(byte_data):
    binary_data = ""
    for byte in byte_data:
        binary_byte = bin(byte)[2:].zfill(8)  # Convert each byte to binary and pad with zeros to make it 8 bits
        binary_data += binary_byte
    return binary_data



def binary_to_bytes2(binary_data):
    binary_data = ''.join(filter(lambda x: x in '01', binary_data))

    byte_data = bytearray()
    for i in range(0, len(binary_data), 8):
        byte = int(binary_data[i:i + 8], 2)
        byte_data.append(byte)

    return bytes(byte_data)





# text in text steganography    
def txt_encode(text):
    l=len(text)
    i=0
    add=''
    while i<l:
        t=ord(text[i])
        if(t>=32 and t<=64):
            t1=t+48
            t2=t1^170       #170: 10101010
            res = bin(t2)[2:].zfill(8)
            add+="0011"+res
        
        else:
            t1=t-48
            t2=t1^170
            res = bin(t2)[2:].zfill(8)
            add+="0110"+res
        i+=1
    res1=add+"111111111111"
    length = len(res1)
    HM_SK=""
    ZWC={"00":u'\u200C',"01":u'\u202C',"11":u'\u202D',"10":u'\u200E'}      
    file1 = open("./resources/cover_text.txt","r+")
    nameoffile = input("\nEnter the name of the Stego file after Encoding(with extension):- ")
    file3= open("./output/"+nameoffile,"w+", encoding="utf-8")
    word=[]
    for line in file1: 
        word+=line.split()
    i=0
    while(i<len(res1)):  
        s=word[int(i/12)]
        j=0
        x=""
        HM_SK=""
        while(j<12):
            x=res1[j+i]+res1[i+j+1]
            HM_SK+=ZWC[x]
            j+=2
        s1=s+HM_SK
        file3.write(s1)
        file3.write(" ")
        i+=12
    t=int(len(res1)/12)     
    while t<len(word): 
        file3.write(word[t])
        file3.write(" ")
        t+=1
    file3.close()  
    file1.close()
    print("\n\n\nText embedded successfully!! Stego file saved as: ./output/"+nameoffile)


def encode_txt_data(password):
    count2=0
    file1 = open(input("Enter the path of cover text file: "),"r")
    for line in file1: 
        for word in line.split():
            count2=count2+1
    file1.close()       
    bt=int(count2)
    print("Maximum number of words that can be inserted :- ",int(bt/6))
    text1=input("\nEnter data to be encoded:- ")
    l=len(text1)
    if(l<=bt):
        key = key_generator(password,'tt')
        encrypted_message = encrypt(key, bytes(text1,"utf-8"),'tt')
        encrypted_message_str = encrypted_message.hex()  # Convert bytes to hexadecimal string
        print("\nInputed message can be hidden in the cover file\n")
        txt_encode(encrypted_message_str)
    else:
        print("\nString is too big please reduce string size")
        encode_txt_data()



def BinaryToDecimal(binary):
    string = int(binary, 2)
    return string



def decode_txt_data(password):
    with open('./output/key_tt.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    password1 = contents[0]
    key = contents[1]
    if str(password1, "utf-8") == password.strip():
        ZWC_reverse={u'\u200C':"00",u'\u202C':"01",u'\u202D':"11",u'\u200E':"10"}
        stego=input("\nPlease enter the stego file path to decode the message:- ")
        file4= open(stego,"r", encoding="utf-8")
        temp=''
        for line in file4: 
            for words in line.split():
                T1=words
                binary_extract=""
                for letter in T1:
                    if(letter in ZWC_reverse):
                         binary_extract+=ZWC_reverse[letter]
                if binary_extract=="111111111111":
                    break
                else:
                    temp+=binary_extract
        lengthd = len(temp)
        i=0
        a=0
        b=4
        c=4
        d=12
        final=''
        while i<len(temp):
            t3=temp[a:b]
            a+=12
            b+=12
            i+=12
            t4=temp[c:d]
            c+=12
            d+=12
            if(t3=='0110'):
                decimal_data = BinaryToDecimal(t4)
                final+=chr((decimal_data ^ 170) + 48)
            elif(t3=='0011'):
                decimal_data = BinaryToDecimal(t4)
                final+=chr((decimal_data ^ 170) - 48)
        decrypted_message = decrypt(key, final, 'tt')
        print("\n\n\nMessage after decoding from the stego file:- ", decrypted_message.decode("utf-8"))
    else:
        print("Invalid Password!!")



def caller_tt():
    while True:
        print("\n\t\tTEXT IN TEXT STEGANOGRAPHY OPERATIONS")
        print("\n\n\t1. Encode Text in Text message")  
        print("\t2. Decode Text from Text message")  
        print("\t3. Exit")  
        choice1 = int(input("\n\t\tEnter your Choice: "))   
        if choice1 == 1:
            password = input("Enter password for encryption: ")
            encode_txt_data(password)
        elif choice1 == 2:
            password = input("Enter password for decryption: ")
            decode_txt_data(password)
        elif choice1 == 3:
            print("\n\nExiting.....")
            break 
        else:
            print("\n\nInvalid Choice!!")





# text in image steganography
def hide_msg_in_image(password):
    msg = bytes(input("Enter message to be encrypted: "), "utf-8")
    path = input("Enter path of cover image: ")
    image = Image.open(path)
    key = key_generator(password,'ti')
    encrypted_message = encrypt(key, msg, 'ti')

    message_blocks = [encrypted_message[i:i + 8] for i in range(0, len(encrypted_message), 8)]
    binary_blocks = [format(int.from_bytes(block, 'big'), '064b') for block in message_blocks]
    pixels = list(image.getdata())
    encoded_pixels = []
    for i, pixel in enumerate(pixels):
        if i < len(binary_blocks):
            encoded_pixel = (pixel[0], pixel[1], pixel[2] | int(binary_blocks[i][-1]))
        else:
            encoded_pixel = pixel
        encoded_pixels.append(encoded_pixel)
    encoded_image = Image.new(image.mode, image.size)
    encoded_image.putdata(encoded_pixels)
    file_name = input("Enter the name of stego file to be generated: ")
    encoded_image.save('./output/'+ file_name)
    print("\n\n\nText embedded successfully!! Stego file saved as: ./output/"+file_name)



def retrieve_msg_from_image(password):
    key,check = checkPass(password,'ti')
    if check == True:
        path = input("Enter path of Stego image: ")
        encoded_image = Image.open(path)
        binary_blocks = []
        for pixel in encoded_image.getdata():
            binary_block = format(pixel[2], '08b')
            binary_blocks.append(binary_block)
        encrypted_message = b''.join([int(block, 2).to_bytes(8, 'big') for block in binary_blocks])
        decrypted_message = decrypt(key, encrypted_message,'ti')
        try:
            message = decrypted_message.decode("utf-8")
            print("\n\n\nMessage after decoding from the stego file:- ", message)
        except Exception as Error:
            print(type(Error).__name__)
            print("\n\n\n This image has nothing to decode!")
            
    else:
        print("Invalid Password!!")



def caller_ti():
    while True:
        print("\n\t\tTEXT IN IMAGE STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Text in Image")  
        print("2. Decode Text from Image")  
        print("3. Exit") 
        ch = int(input("Enter your Choice: "))
        if ch == 1:
            password = input("Enter password for encryption: ")
            hide_msg_in_image(password)

        elif ch == 2:
            password = input("Enter password for decryption: ")
            retrieve_msg_from_image(password)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")



        

# image in image steganography
def encode_image_in_image(password):
    image_to_hide_path = input("Enter path of image to be hidden: ")
    image_to_hide_in_path = input("Enter path to cover image: ")
    encoded_image_path = "./output/"+input("Enter the name of stego file to be generated: ")
    n_bits = 1
    image_to_hide = Image.open(image_to_hide_path)
    image_to_hide_in = Image.open(image_to_hide_in_path)
    width, height = image_to_hide.size
    hide_image = image_to_hide.load()
    hide_in_image = image_to_hide_in.load()

    data = []

    key = key_generator(password,'ii')
    image_bytes = image_to_hide.tobytes()
    encrypted_image = encrypt(key, image_bytes,'ii')

    encrypted_iterator = iter(encrypted_image)

    for y in range(height):
        for x in range(width):
            try:
                r_byte = next(encrypted_iterator)
                g_byte = next(encrypted_iterator)
                b_byte = next(encrypted_iterator)

                r_hide_pixel = get_n_most_significant_bits(r_byte, n_bits)
                g_hide_pixel = get_n_most_significant_bits(g_byte, n_bits)
                b_hide_pixel = get_n_most_significant_bits(b_byte, n_bits)

                r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]
                r_hide_in = remove_n_least_significant_bits(r_hide_in, n_bits)
                g_hide_in = remove_n_least_significant_bits(g_hide_in, n_bits)
                b_hide_in = remove_n_least_significant_bits(b_hide_in, n_bits)

                data.append((r_hide_pixel + r_hide_in, g_hide_pixel + g_hide_in, b_hide_pixel + b_hide_in))
            except StopIteration:
                break
    
    make_image(data, image_to_hide.size).save(encoded_image_path)
    print("\n\nImage embedded successfully!! Stego file saved as: ",encoded_image_path)



def decode_image_from_image(password):
    key,check = checkPass(password,'ii')
    if check == True:
        encoded_image_path = input("Enter the path of Stego image: ")
        decoded_image_path = "./output/"+input("Enter the name of output file to be generated: ")
        n_bits = 1
        image_to_decode = Image.open(encoded_image_path)
        width, height = image_to_decode.size
        encoded_image = image_to_decode.load()

        data = []

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

        decrypted_image = make_image(data, image_to_decode.size)
        decrypted_image_bytes = decrypted_image.tobytes()
        original_image_bytes = decrypt(key, decrypted_image_bytes,"ii")
        original_image = Image.frombytes("RGB", decrypted_image.size, original_image_bytes)
        original_image.save(decoded_image_path)
        print("\n\n\nImage extracted successfully! Output file saved as: ",decoded_image_path)
    else:
        print("Invalid Password!!")
        return 0



def caller_ii():
    while True:
        print("\n\t\tIMAGE IN IMAGE STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Image in Image")  
        print("2. Decode Image from Image")  
        print("3. Exit") 
        ch = int(input("\n\t\t Enter your choice: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            encode_image_in_image(password)

        elif ch == 2:
            password = input("Enter password for decryption: ")
            decode_image_from_image(password)
            
        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")






# audio in image steganography
def encode_audio_in_image(password):
    audio_to_hide_path = input("Enter path of audio to be hidden: ")
    image_to_hide_in_path = input("Enter path of cover image: ")
    encoded_image_path = "./output/"+input("Enter the name of stego file to be generated: ")
    n_bits = 1
    image_to_hide_in = Image.open(image_to_hide_in_path)
    width, height = image_to_hide_in.size
    hide_in_image = image_to_hide_in.load()

    with wave.open(audio_to_hide_path, 'rb') as secret_audio_file:
        secret_frames = secret_audio_file.readframes(-1)

    key = key_generator(password,'ai')
    encrypted_audio = encrypt(key, secret_frames, 'ai')

    data = []

    a = 0
    b = 0

    encrypted_iterator = iter(encrypted_audio)
    for y in range(height):
        for x in range(width):
            try:
                r_byte = next(encrypted_iterator)
                g_byte = next(encrypted_iterator)
                b_byte = next(encrypted_iterator)
    
                r_hide_pixel = get_n_most_significant_bits(r_byte, n_bits)
                g_hide_pixel = get_n_most_significant_bits(g_byte, n_bits)
                b_hide_pixel = get_n_most_significant_bits(b_byte, n_bits)
    
                r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]
                r_hide_in = remove_n_least_significant_bits(r_hide_in, n_bits)
                g_hide_in = remove_n_least_significant_bits(g_hide_in, n_bits)
                b_hide_in = remove_n_least_significant_bits(b_hide_in, n_bits)
    
                data.append((r_hide_pixel + r_hide_in, g_hide_pixel + g_hide_in, b_hide_pixel + b_hide_in))
                
            except StopIteration:
                break
            a+=1
        b+=1


    for y in range(b,height):
        for x in range(a,width):
            r_hide_in, g_hide_in, b_hide_in = hide_in_image[x, y]
            data.append((r_hide_in, g_hide_in, b_hide_in))

    
    make_image(data, image_to_hide_in.size).save(encoded_image_path)
    print("\n\nAudio embedded successfully!!! Stego file saved as: ",encoded_image_path)



def decode_audio_from_image(password):
    key,check = checkPass(password,'ai')
    if check == True:
        encoded_image_path = input("Enter the path of Stego image: ")
        decoded_audio_path = "./output/"+input("Enter the name of output file to be generated: ")
        n_bits = 1

        image_to_decode = Image.open(encoded_image_path)
        width, height = image_to_decode.size
        encoded_image = image_to_decode.load()

        extracted_audio_frames = bytearray()

        for y in range(height):
            for x in range(width):
                r_encoded, g_encoded, b_encoded = encoded_image[x, y]

                r_encoded = get_n_least_significant_bits(r_encoded, n_bits)
                g_encoded = get_n_least_significant_bits(g_encoded, n_bits)
                b_encoded = get_n_least_significant_bits(b_encoded, n_bits)

                original_byte = r_encoded | g_encoded | b_encoded

                extracted_audio_frames.append(original_byte)

        decrypted_audio = decrypt(key, extracted_audio_frames,"ai")

        with wave.open(decoded_audio_path, 'wb') as output_audio_file:
            output_audio_file.setnchannels(2)  # Specify the number of channels
            output_audio_file.setframerate(22050)
            output_audio_file.setsampwidth(2)  # Set sample width to 2 bytes for 16-bit audio
            output_audio_file.writeframes(decrypted_audio)

        print("\n\n\nAudio extracted successfully! Output file saved as:", decoded_audio_path)
    else:
        print("Invalid Password!!")



def caller_ai():
    while True:
        print("\n\t\tAUDIO IN IMAGE STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Audio in Image")  
        print("2. Decode Audio from Image")  
        print("3. Exit") 
        ch = int(input("\n\t\t Enter your choice: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            encode_audio_in_image(password)

        elif ch == 2:
            password = input("Enter password for decryption: ")
            decode_audio_from_image(password)
            
        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")






# text in audio steganography
def hide_text_in_audio(password):
    audio_file = input("Enter path of cover Audio: ")
    message = bytes(input("Enter the text message to hide: "), "utf-8")
    output_file = input("Enter the name stego file with extension: ")
    audio = wave.open(audio_file, 'rb')
    frames = audio.readframes(-1)

    key = key_generator(password,'ta')
    encrypted_message = encrypt(key, message,'ta')

    if len(encrypted_message) > len(frames) * 8:
        raise Exception("Message too long to hide in this audio file")

    encoded_frames = bytearray(frames)
    message_index = 0
    for i in range(len(encoded_frames)):
        if message_index < len(encrypted_message):
            encoded_frames[i] = (encoded_frames[i] & 0xFE) | int(
                encrypted_message[message_index])
            message_index += 1

    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = script_dir + "\output"
    output_path = os.path.join(script_dir, output_file)

    with wave.open(output_path, 'wb') as output:
        output.setparams(audio.getparams())
        output.writeframes(encoded_frames)
    print("\n\n\nText embedded successfully! Stego file saved as: ", output_path)



def extract_text_from_audio(password):
    key,check = checkPass(password,'ta')
    if check == True:
        encoded_audio_file = input("Enter the path of the Stego audio: ")
        audio = wave.open(encoded_audio_file, 'rb')
        frames = audio.readframes(-1)

        encrypted_message = ""
        message = ""
        consecutive_zeros = 0

        for frame in frames:
            bit = frame & 1
            encrypted_message += str(bit)
            if bit == 0:
                consecutive_zeros += 1
            else:
                consecutive_zeros = 0
            if consecutive_zeros == 8:
                break
        decrypted_message = decrypt(key, encrypted_message, 'ta')
        message = decrypted_message.decode("utf-8")
        print("\n\n\nMessage decoded from the stego file:- ", message) 
    else:
        print("Invalid Password!!")



def caller_ta():
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
            password = input("Enter password for decryption: ")
            extract_text_from_audio(password)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")






# image in audio steganography
def hide_image_in_audio(password):
    audio_file= input("Enter path of cover Audio: ")
    image_to_hide_path = input("Enter path of image to be hidden: ")
    image = Image.open(image_to_hide_path)
    output_file = input("Enter the name stego file with extension to be generated: ")
    audio = wave.open(audio_file, 'rb')
    frames = audio.readframes(-1)

    key = key_generator(password, 'ia')
    image_bytes = image.tobytes()
    encrypted_image = encrypt(key, image_bytes, 'ia')

    if len(encrypted_image) > len(frames) * 8:
        raise Exception("Message too long to hide in this audio file")
    encoded_frames = bytearray(frames)
    message_index = 0

    total_frames = len(encoded_frames)
    encrypted_image_size = len(encrypted_image)
    gap_size = max(1, total_frames // encrypted_image_size)

    for i in range(0, len(encoded_frames), gap_size):
        if message_index < len(encrypted_image):
            encoded_frames[i] = (encoded_frames[i] & 0xFE) | int(encrypted_image[message_index])
            message_index += 1

    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = script_dir + "\output"
    output_path = os.path.join(script_dir, output_file)

    with wave.open(output_path, 'wb') as output:
        output.setparams(audio.getparams())
        output.writeframes(encoded_frames)

    print("\n\n\nImage embedded successfully! Stego file saved as: ", output_path)
    return gap_size, image.size



def extract_image_from_audio(password, gap_index, size):
    key,check = checkPass(password,'ia')
    if check == True:
        encoded_audio_file = input("Enter the path of the Stego audio: ")
        decoded_image_path = "./output/"+input("Enter the name of output file to be generated: ")
        audio = wave.open(encoded_audio_file, 'rb')
        frames = audio.readframes(-1)
        encrypted_image = ""
        message = ""
        consecutive_zeros = 0
    
        for i in range(0, len(frames), gap_index):
            frame = frames[i]

            bit = frame & 1
            encrypted_image += str(bit)
 
            if bit == 0:
                consecutive_zeros += 1
            else:
                consecutive_zeros = 0

            if consecutive_zeros == 8:
                break

        encrypted_image = encrypted_image[:-(consecutive_zeros)]
  
        decrypted_image_bytes = decrypt(key, encrypted_image, "ia")
        Image.frombytes("RGB", size, decrypted_image_bytes).save(decoded_image_path)
        print("\n\n\nImage extracted successfully! Output file saved as: ", decoded_image_path)
    else:
        print("Invalid Password!!")



def caller_ia():
    gap_size = 0
    while True:
        print("\n\t\tIMAGE IN AUDIO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Image in Audio")  
        print("2. Decode Image from Audio")  
        print("3. Exit")
        ch = int(input("\n\t\tChoose from below options: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            gap_size,size = hide_image_in_audio(password) 

        elif ch == 2:
            password = input("Enter password for decryption: ")
            extract_image_from_audio(password, gap_size, size)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")





# audio in audio steganography
def hide_audio_in_audio(password):
    cover_audio= input("Enter path of cover Audio: ")
    secret_audio = input("Enter path of audio to be hidden: ")
    output_file = "./output/"+input("Enter the name stego file with extension to be generated: ")
    with wave.open(cover_audio, 'rb') as cover_audio_file:
        cover_frames = cover_audio_file.readframes(-1)

    with wave.open(secret_audio, 'rb') as secret_audio_file:
        secret_frames = secret_audio_file.readframes(-1)

    key = key_generator(password,'aa')
    encrypted_audio = encrypt(key, secret_frames,'aa')

    if len(encrypted_audio) < len(cover_frames):
        encrypted_audio += b'\0' * (len(cover_frames) - len(encrypted_audio))

    encoded_frames = bytearray(cover_frames)
    for i in range(len(encrypted_audio)):
        encoded_frames[i] = (encoded_frames[i] & 0xFE) | (encrypted_audio[i] >> 7)

    with wave.open(output_file, 'wb') as output:
        output.setparams(cover_audio_file.getparams())
        output.writeframes(encoded_frames)

    print("\n\n\nAudio embedded successfully! Output file saved as:", output_file)

    

def extract_audio_from_audio(password):
    key,check = checkPass(password,'aa')
    if check == True:
        encoded_audio_file = input("Enter the path of the encoded audio file: ")
        decoded_audio_path = "./output/"+input("Enter the name of output file with extension to be generated: ")
        with wave.open(encoded_audio_file, 'rb') as audio_file:
            frames = audio_file.readframes(-1)

        encrypted_audio = b""
        consecutive_zeros = 0

        for frame in frames:
            bit = frame & 1
            encrypted_audio += bytes([bit])

            if bit == 0:
                consecutive_zeros += 1
            else:
                consecutive_zeros = 0

            if consecutive_zeros == 8:
                break

        encrypted_audio = encrypted_audio[:-(consecutive_zeros)]

        decrypted_audio_bytes = decrypt(key, encrypted_audio,"aa")

        with wave.open(decoded_audio_path, 'wb') as output_audio_file:
            output_audio_file.setparams(audio_file.getparams())
            output_audio_file.setframerate(22050)
            output_audio_file.writeframes(decrypted_audio_bytes)

        print("\n\n\nAudio extracted successfully! Output file saved as: ", decoded_audio_path)
    else:
        print("Invalid Password!!")



def caller_aa():
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





# text in video steganography
def embed_text_in_video(frame,password):
    msg = bytes(input("Enter the text message to hide: "), "utf-8")
    key = key_generator(password,"tv")
    encrypted_message = encrypt(key, msg, "tv")
    if (len(encrypted_message) == 0): 
        raise ValueError('Data entered to be encoded is empty')
    
    binary_data = bytes_to_binary2(encrypted_message)
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



def extract_text_from_video(frame,key):
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
                final_decoded_msg = binary_to_bytes2(final_decoded_msg)
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
            change_frame_with = embed_text_in_video(frame,password)
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
                extract_text_from_video(frame,key)
                return
    else:
        print("Invalid Password!!")
    


def caller_tv():
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




# image in video steganography
def embed_image(frame, password):
    image_path = input("Enter path of image to be hidden: ")
    key = key_generator(password,"iv")
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
    decoded_data_list = []
    total_bytes = []

    for i in frame:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            data_binary += r[-1]
            data_binary += g[-1]
            data_binary += b[-1]

            if len(data_binary) >= 8:
                byte = int(data_binary[:8], 2)
                total_bytes.append(byte)
                data_binary = data_binary[8:]

    if data_binary:
        byte = int(data_binary.ljust(8, '0'), 2)
        total_bytes.append(byte)

    final_decoded_img = bytes(total_bytes)
    decrypted_image = decrypt_image(key, final_decoded_img, image_shape)
    return decrypted_image



def encode_vid_image(password):
    cover_video = input("Enter path of cover video: ")
    cap = cv2.VideoCapture(cover_video)
    vidcap = cv2.VideoCapture(cover_video)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    frame_width = int(vidcap.get(3))
    frame_height = int(vidcap.get(4))

    size = (frame_width, frame_height)
    stego_video = "./output/" + input("Enter name of Stego video with extension to be generated: ")
    out = cv2.VideoWriter(stego_video, fourcc, 25.0, size)
    max_frame = 0

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        max_frame += 1
    cap.release()
    print("Total number of Frame in selected Video: ", max_frame)
    n = int(input("Enter the frame number where you want to embed data: "))
    frame_number = 0

    while(vidcap.isOpened()):
        frame_number += 1
        ret, frame = vidcap.read()
        if ret == False:
            break
        if frame_number == n:
            frame, image_shape = embed_image(frame, password)
        out.write(frame)

    print("\n\n\nImage embedded successfully! Stego video saved as: ",stego_video)
    return image_shape




def decode_vid_image(password, image_shape):
    key,check = checkPass(password,'iv')
    if check == True:
        stego_video = input("Enter path of Stego video: ")
        output_image_path = "./output/"+input("Enter the name of output file with extension to be generated: ")
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
                cv2.imwrite(output_image_path, extracted_image)
                print("\n\n\nImage extracted successfully! Output file saved as: ",output_image_path)
    else:
        print("Invalid Password!!")



def caller_iv():
    while True:
        print("\n\t\tIMAGE IN VIDEO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Image in Video")  
        print("2. Decode Image from Video")  
        print("3. Exit")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1:
            password = input("Enter password for encryption: ")
            img_shape = encode_vid_image(password)
        elif choice1 == 2:
            password = input("Enter password for decryption: ")
            decode_vid_image(password, img_shape)
        elif choice1 == 3:
            print("\n\nExiting.....")
            break
        else:
            print("Incorrect Choice")
        print("\n")






# audio in video
def hide_audio_in_audio2(cover_audio, secret_audio, output_file, password):
    with wave.open(cover_audio, 'rb') as cover_audio_file:
        cover_frames = cover_audio_file.readframes(-1)

    with wave.open(secret_audio, 'rb') as secret_audio_file:
        secret_frames = secret_audio_file.readframes(-1)

    key = key_generator(password,"av")
    encrypted_audio = encrypt(key, secret_frames, "av")

    if len(encrypted_audio) < len(cover_frames):
        encrypted_audio += b'\0' * (len(cover_frames) - len(encrypted_audio))

    encoded_frames = bytearray(cover_frames)
    for i in range(len(encrypted_audio)):
        encoded_frames[i] = (encoded_frames[i] & 0xFE) | (encrypted_audio[i] >> 7)

    with wave.open(output_file, 'wb') as output:
        output.setparams(cover_audio_file.getparams())
        output.writeframes(encoded_frames)
    os.remove(cover_audio)



def extract_audio_from_audio2(encoded_audio_file, decoded_audio_path, password, key):
    with wave.open(encoded_audio_file, 'rb') as audio_file:
        frames = audio_file.readframes(-1)

    encrypted_audio = b""
    consecutive_zeros = 0

    for frame in frames:
        bit = frame & 1
        encrypted_audio += bytes([bit])

        if bit == 0:
            consecutive_zeros += 1
        else:
            consecutive_zeros = 0

        if consecutive_zeros == 8:
            break

    encrypted_audio = encrypted_audio[:-(consecutive_zeros)]

    decrypted_audio_bytes = decrypt(key, encrypted_audio, "av")

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
    normalized_audio.export(audio_path, format='wav') 



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
    capture = cv2.VideoCapture(og_path) 
    fps = capture.get(cv2.CAP_PROP_FPS) 

    video_path_real = frames_directory + "\\%d.png" 

    os.system(
        f"ffmpeg -framerate {int(fps)} -i \"{video_path_real}\" -codec copy output\\combined_video_only.mkv") 
    os.system(
        f"ffmpeg -i output\\combined_video_only.mkv -i \"{audio_path}\" -codec copy \"{output}\"") 
    
    shutil.rmtree(frames_directory, ignore_errors=True)
    os.remove(audio_path)
    os.remove("./output/combined_video_only.mkv")             



def hide_audio_in_video(password):
    og_video = input("Enter path of cover video: ")
    og_audio = input("Enter path of audio file to be hidden: ")
    output_video = input("Enter the name of Stego file to be generated: ")
    base_filename = os.path.splitext(os.path.basename(og_video))[0]
    video_object = VideoFileClip(og_video)

    frames_directory = get_frames(video_object, base_filename)

    get_audio(base_filename, video_object) 
    cover_audio = f'output\\{base_filename}_audio.wav'

    output_file = "./output/output_test999.wav"       

    hide_audio_in_audio2(cover_audio, og_audio, output_file, password) 

    encoded_audio_data = "./output/output_test999.wav" 
    output = "./output/"+output_video
    combine_audio_video(frames_directory, encoded_audio_data, og_video, output)
    print("\n\n\nAudio embeded successfully! Stego video saved as: ", output)


    
def unhide_audio_from_encryptedVideo(password):
    key,check = checkPass(password,'av')
    if check == True:
        encrypted_video = input("Enter encrypted video file path: ")
        output_audio = input("Enter the name of output audio file to be generated: ")
        base_filename = os.path.splitext(os.path.basename(encrypted_video))[0]
        video_object = VideoFileClip(encrypted_video)

        get_audio(base_filename, video_object)
        extracted_audio = f'output\\{base_filename}_audio.wav'

        decoded_audio_path = "./output/"+output_audio
        extract_audio_from_audio2(extracted_audio, decoded_audio_path, password, key)

        print("\n\n\nAudio extracted successfully! Output file saved as: ",decoded_audio_path)
    
    else:
        print("Invalid Password!!")



def caller_av():
    while True:
        print("\n\t\tAUDIO IN VIDEO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Audio in video")  
        print("2. Decode Audio from Video")  
        print("3. Exit")  
        option = int(input("Enter the Choice: "))

        if option == 1:
            password = input("Enter password for encryption: ")
            hide_audio_in_video(password)

        elif option == 2:
            password = input("Enter password for decryption: ")
            unhide_audio_from_encryptedVideo(password)

        elif option == 3:
            print("\n\nExiting.....")
            break

        else:
            print("Incorrect Choice!!")






# main
def print_header():
    print("\n")
    print("╔" + "═" * 80 + "╗")
    print("║" + " " * 26 + "MULTIMEDIA STEGANOGRAPHY TOOL" + " " * 25 + "║")
    print("╚" + "═" * 80 + "╝")

def print_options():
    print("\n\nOptions:")
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║ 1. Text in Text Steganography                                                  ║")
    print("║                                                                                ║")
    print("║ 2. Text in Image Steganography                                                 ║")
    print("║ 3. Image in Image Steganography                                                ║")
    print("║ 4. Audio in Image Steganography                                                ║")
    print("║                                                                                ║")
    print("║ 5. Text in Audio Steganography                                                 ║")
    print("║ 6. Image in Audio Steganography                                                ║")
    print("║ 7. Audio in Audio Steganography                                                ║")
    print("║                                                                                ║")
    print("║ 8. Text in Video Steganography                                                 ║")
    print("║ 9. Image in Video Steganography                                                ║")
    print("║ 10. Audio in Video Steganography                                               ║")
    print("║                                                                                ║")
    print("║ 11. Exit                                                                       ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")

def main():
    CD = os.getcwd()
    os.makedirs(os.path.join(CD,"output"), exist_ok=True)
    print_header()
    while True:
        print_options()
        ch = int(input("\n\t\tChoose from above options: "))
        if ch == 1:
            caller_tt()
        elif ch == 2:
            caller_ti()
        elif ch == 3:
            caller_ii()
        elif ch == 4:
            caller_ai()
        elif ch == 5:
            caller_ta()
        elif ch == 6:
            caller_ia()
        elif ch == 7:
            caller_aa()
        elif ch == 8:
            caller_tv()
        elif ch == 9:
            caller_iv()
        elif ch == 10:
            caller_av()
        elif ch == 11:
            print("\n\nExiting.....")
            break
        else:
            print("\n\nInvalid Choice!!")

if __name__ == "__main__":
    main()   
