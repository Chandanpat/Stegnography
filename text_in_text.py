import numpy as np
from essentials import *


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
    print("\n\n\nText embedded successfully!! Stego file saved as: ./output/",nameoffile)


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


def caller():
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

