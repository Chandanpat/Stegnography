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
    # print(type(msg))
    cipher = AES.new(key, AES.MODE_CBC)
    ciphered_data = cipher.encrypt(pad(msg, AES.block_size))
    # print(ciphered_data)
    with open('./output/encrypted_tt.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphered_data)
    return ciphered_data


def key_generator(password):
    simple_key = get_random_bytes(32)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('./output/key_tt.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key


def decrypt(key, cypherText):
    with open('./output/encrypted_tt.bin', 'rb') as f:
        iv = f.read(16)
        cypherText = f.read()
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        og = unpad(cipher.decrypt(cypherText), AES.block_size)
    return og


# # def txt_encode(encrypted_message):
# #     res1 = ''.join(format(byte, '08b') for byte in encrypted_message)
# #     print(res1)
# #     print("The string after binary conversion applying all the transformations:", res1)
# #     length = len(res1)
# #     print("Length of binary after conversion:", length)
    
# #     HM_SK = ""
# #     ZWC = {"00": u'\u200C', "01": u'\u202C', "11": u'\u202D', "10": u'\u200E'}
    
# #     file1 = open("./resources/cover_text.txt", "r+")
# #     nameoffile = input("\nEnter the name of the Stego file after Encoding (with extension): ")
# #     file3 = open("./output/" + nameoffile, "w+", encoding="utf-8")
# #     word = []
    
# #     for line in file1:
# #         word += line.split()
    
# #     i = 0
# #     while i < len(res1):
# #         s = word[i // 12]
# #         j = 0
# #         HM_SK = ""
# #         while j < 12:
# #             x = res1[i:i + 2]
# #             if x:
# #                 HM_SK += ZWC[x]
# #             i += 2
# #             j += 1
# #         s1 = s + HM_SK
# #         file3.write(s1)
# #         file3.write(" ")
    
# #     t = len(res1) // 12
# #     while t < len(word):
# #         file3.write(word[t])
# #         file3.write(" ")
# #         t += 1
    
# #     file3.close()
# #     file1.close()
# #     print("\nStego file has been successfully generated")

# def txt_encode(text):
#     l=len(text)
#     i=0
#     add=''
#     while i<l:
#         t=ord(text[i])
#         if(t>=32 and t<=64):
#             t1=t+48
#             t2=t1^170       #170: 10101010
#             res = bin(t2)[2:].zfill(8)
#             add+="0011"+res
        
#         else:
#             t1=t-48
#             t2=t1^170
#             res = bin(t2)[2:].zfill(8)
#             add+="0110"+res
#         i+=1
#     res1=add+"111111111111"
#     print("The string after binary conversion appyling all the transformation :- " + (res1))   
#     length = len(res1)
#     print("Length of binary after conversion:- ",length)
#     HM_SK=""
#     ZWC={"00":u'\u200C',"01":u'\u202C',"11":u'\u202D',"10":u'\u200E'}      
#     file1 = open("./resources/cover_text.txt","r+")
#     nameoffile = input("\nEnter the name of the Stego file after Encoding(with extension):- ")
#     file3= open("./output/"+nameoffile,"w+", encoding="utf-8")
#     word=[]
#     for line in file1: 
#         word+=line.split()
#     i=0
#     while(i<len(res1)):  
#         s=word[int(i/12)]
#         j=0
#         x=""
#         HM_SK=""
#         while(j<12):
#             x=res1[j+i]+res1[i+j+1]
#             HM_SK+=ZWC[x]
#             j+=2
#         s1=s+HM_SK
#         file3.write(s1)
#         file3.write(" ")
#         i+=12
#     t=int(len(res1)/12)     
#     while t<len(word): 
#         file3.write(word[t])
#         file3.write(" ")
#         t+=1
#     file3.close()  
#     file1.close()
#     print("\nStego file has successfully generated")

# def encode_txt_data(password):
#     count2=0
#     file1 = open("./resources/cover_text.txt","r")
#     for line in file1: 
#         for word in line.split():
#             count2=count2+1
#     file1.close()       
#     bt=int(count2)
#     print("Maximum number of words that can be inserted :- ",int(bt/6))
#     text1=bytes(input("\nEnter data to be encoded:- "), "utf-8")
#     l=len(text1)
#     if(l<=bt):
#         print("\nInputed message can be hidden in the cover file\n")
#         # key generation and encryption before encoding
#         key = key_generator(password)
#         print(key)
#         encrypted_message = encrypt(key, text1)
#         print(len(text1), len(encrypted_message))
#         txt_encode(encrypted_message)
#     else:
#         print("\nString is too big please reduce string size")
#         encode_txt_data()



# def BinaryToDecimal(binary):
#     string = int(binary, 2)
#     return string



# def decode_txt_data(password):
#     ZWC_reverse={u'\u200C':"00",u'\u202C':"01",u'\u202D':"11",u'\u200E':"10"}
#     stego=input("\nPlease enter the stego file name(with extension) to decode the message:- ")
#     file4= open(stego,"r", encoding="utf-8")
#     temp=''
#     for line in file4: 
#         for words in line.split():
#             T1=words
#             binary_extract=""
#             for letter in T1:
#                 if(letter in ZWC_reverse):
#                      binary_extract+=ZWC_reverse[letter]
#             if binary_extract=="111111111111":
#                 break
#             else:
#                 temp+=binary_extract
#     print("\nEncrypted message presented in code bits:",temp) 
#     lengthd = len(temp)
#     print("\nLength of encoded bits:- ",lengthd)
#     i=0
#     a=0
#     b=4
#     c=4
#     d=12
#     encrypted_message=''
#     while i<len(temp):
#         t3=temp[a:b]
#         a+=12
#         b+=12
#         i+=12
#         t4=temp[c:d]
#         c+=12
#         d+=12
#         if(t3=='0110'):
#             decimal_data = BinaryToDecimal(t4)
#             encrypted_message+=chr((decimal_data ^ 170) + 48)
#         elif(t3=='0011'):
#             decimal_data = BinaryToDecimal(t4)
#             encrypted_message+=chr((decimal_data ^ 170) - 48)
#         print("\nMessage after decoding from the stego file:- ",encrypted_message)

#     # password verification and decrypting after decoding message
#     # with open('./output/key_tt.bin', 'rb') as f:
#     #     data = f.read()
#     # contents = data.splitlines()
#     # # print(contents)
#     # password1 = contents[0]
#     # key = contents[1]
#     # # print(key)
#     # # print(str(password1, "utf-8"), "\n", password.strip())
#     # if str(password1, "utf-8") == password.strip():
#     #     decrypted_message = decrypt(key, encrypted_message)
#     #     message = decrypted_message.decode("utf-8")
#     #     print("\nMessage after decoding from the stego file:- ",message)
#     # else:
#     #     print("Invalid Password!!")


    

# def caller():
#     while True:
#         # print("\n\t\tTEXT STEGANOGRAPHY OPERATIONS")
#         print("\n\n\t1. Embed Text in Text message")  
#         print("\t2. Extract Text from Text message")  
#         print("\t3. Exit")  
#         choice1 = int(input("\n\t\tEnter your Choice:"))   
#         if choice1 == 1:
#             password = input("Enter password for encryption: ")
#             encode_txt_data(password)
#         elif choice1 == 2:
#             password = input("Enter password for decryption: ")
#             decode_txt_data(password)
#         elif choice1 == 3:
#             print("\n\nExiting.....")
#             break 
#         else:
#             print("\n\nInvalid Choice!!")



# # def msgtobinary(msg):
# #     if type(msg) == str:
# #         result= ''.join([ format(ord(i), "08b") for i in msg ])
    
# #     elif type(msg) == bytes or type(msg) == np.ndarray:
# #         result= [ format(i, "08b") for i in msg ]
    
# #     elif type(msg) == int or type(msg) == np.uint8:
# #         result=format(msg, "08b")

# #     else:
# #         raise TypeError("Input type is not supported in this function")
    
# #     return result                




# # def caller():
# #     print("\t\t      STEGANOGRAPHY")   
# #     while True:  
# #         print("\n\t\t\tMAIN MENU\n")  
# #         print("1. TEXT STEGANOGRAPHY {Hiding Text in Text cover file}")  
# #         print("2. Exit\n") 
# #         choice1 = int(input("Enter the Choice: ")) 
# #         if choice1 == 1:
# #             txt_steg()
# #         elif choice1 == 2:
# #             break
# #         else:
# #             print("Incorrect Choice")
# #         print("\n\n")   









import numpy as np
import pandas as pand
import os
import cv2
from matplotlib import pyplot as plt

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
    print("The string after binary conversion appyling all the transformation :- " + (res1))   
    length = len(res1)
    print("Length of binary after conversion:- ",length)
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
    print("\n\nStego file has successfully generated. Use ./output/",nameoffile," for decoding")

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
        key = key_generator(password)
        # print(key)
        encrypted_message = encrypt(key, bytes(text1,"utf-8"))
        print("\nInputed message can be hidden in the cover file\n")
        txt_encode(text1)
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
    # print(contents)
    password1 = contents[0]
    key = contents[1]
    # print(key)
    # print(str(password1, "utf-8"), "\n", password.strip())
    if str(password1, "utf-8") == password.strip():
        ZWC_reverse={u'\u200C':"00",u'\u202C':"01",u'\u202D':"11",u'\u200E':"10"}
        stego="./output/" + input("\nPlease enter the stego file name(with extension) to decode the message:- ")
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
        print("\nEncrypted message presented in code bits:",temp) 
        lengthd = len(temp)
        print("\nLength of encoded bits:- ",lengthd)
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
        print("\nMessage after decoding from the stego file:- ",final)
    else:
        print("Invalid Password!!")



def caller():
    while True:
        # print("\n\t\tTEXT STEGANOGRAPHY OPERATIONS")
        print("\n\n\t1. Embed Text in Text message")  
        print("\t2. Extract Text from Text message")  
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




# def caller():
#     print("\t\t      STEGANOGRAPHY")   
#     while True:  
#         print("\n\t\t\tMAIN MENU\n")  
#         print("1. TEXT STEGANOGRAPHY {Hiding Text in Text cover file}")  
#         print("2. Exit\n") 
#         choice1 = int(input("Enter the Choice: ")) 
#         if choice1 == 1:
#             txt_steg()
#         elif choice1 == 2:
#             break
#         else:
#             print("Incorrect Choice")
#         print("\n\n")   