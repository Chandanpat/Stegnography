from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


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
        # with open('./output/c1.txt','wt') as f:
        #     f.write(str(cypher,'utf-8'))
        # with open('./output/c2.txt','wt') as f:
        #     f.write(str(cypherText,'utf-8'))
        # if(cypherText == cypher):
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        og = unpad(cipher.decrypt(cypherText), AES.block_size)
        return og
        # else:
        #     return ""
            


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
        return '',False
    