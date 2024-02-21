import cv2
import os
import shutil
import sys
from datetime import datetime
from multiprocessing import Pool
from functools import partial
import tqdm
from PIL import Image
import numpy as np
# from dnacryptograpy import DNAencrypt, DNAdecrypt
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import padding
# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
from distutils.log import error
from collections import deque
from datetime import datetime


def indexTable(key):
    key = key - 1
    defaultTable = ["AAAA", "AAAC", "AAAG", "AAAT", "AACA", "AACC", "AACG", "AACT", "AAGA", "AAGC", "AAGG", "AAGT", "AATA", "AATC", "AATG", "AATT", "ACAA", "ACAC", "ACAG", "ACAT", "ACCA", "ACCC", "ACCG", "ACCT", "ACGA", "ACGC", "ACGG", "ACGT", "ACTA", "ACTC", "ACTG", "ACTT",
                    "CAAA", "CAAC", "CAAG", "CAAT", "CACA", "CACC", "CACG", "CACT", "CAGA", "CAGC", "CAGG", "CAGT", "CATA", "CATC", "CATG", "CATT", "CCAA", "CCAC", "CCAG", "CCAT", "CCCA", "CCCC", "CCCG", "CCCT", "CCGA", "CCGC", "CCGG", "CCGT", "CCTA", "CCTC", "CCTG", "CCTT",
                    "GAAA", "GAAC", "GAAG", "GAAT", "GACA", "GACC", "GACG", "GACT", "GAGA", "GAGC", "GAGG", "GAGT", "GATA", "GATC", "GATG", "GATT", "GCAA", "GCAC", "GCAG", "GCAT", "GCCA", "GCCC", "GCCG", "GCCT", "GCGA", "GCGC", "GCGG", "GCGT", "GCTA", "GCTC", "GCTG", "GCTT",
                    "TAAA", "TAAC", "TAAG", "TAAT", "TACA", "TACC", "TACG", "TACT", "TAGA", "TAGC", "TAGG", "TAGT", "TATA", "TATC", "TATG", "TATT", "TCAA", "TCAC", "TCAG", "TCAT", "TCCA", "TCCC", "TCCG", "TCCT", "TCGA", "TCGC", "TCGG", "TCGT", "TCTA", "TCTC", "TCTG", "TCTT",
                    "AGAA", "AGAC", "AGAG", "AGAT", "AGCA", "AGCC", "AGCG", "AGCT", "AGGA", "AGGC", "AGGG", "AGGT", "AGTA", "AGTC", "AGTG", "AGTT", "ATAA", "ATAC", "ATAG", "ATAT", "ATCA", "ATCC", "ATCG", "ATCT", "ATGA", "ATGC", "ATGG", "ATGT", "ATTA", "ATTC", "ATTG", "ATTT",
                    "CGAA", "CGAC", "CGAG", "CGAT", "CGCA", "CGCC", "CGCG", "CGCT", "CGGA", "CGGC", "CGGG", "CGGT", "CGTA", "CGTC", "CGTG", "CGTT", "CTAA", "CTAC", "CTAG", "CTAT", "CTCA", "CTCC", "CTCG", "CTCT", "CTGA", "CTGC", "CTGG", "CTGT", "CTTA", "CTTC", "CTTG", "CTTT",
                    "GGAA", "GGAC", "GGAG", "GGAT", "GGCA", "GGCC", "GGCG", "GGCT", "GGGA", "GGGC", "GGGG", "GGGT", "GGTA", "GGTC", "GGTG", "GGTT", "GTAA", "GTAC", "GTAG", "GTAT", "GTCA", "GTCC", "GTCG", "GTCT", "GTGA", "GTGC", "GTGG", "GTGT", "GTTA", "GTTC", "GTTG", "GTTT",
                    "TGAA", "TGAC", "TGAG", "TGAT", "TGCA", "TGCC", "TGCG", "TGCT", "TGGA", "TGGC", "TGGG", "TGGT", "TGTA", "TGTC", "TGTG", "TGTT", "TTAA", "TTAC", "TTAG", "TTAT", "TTCA", "TTCC", "TTCG", "TTCT", "TTGA", "TTGC", "TTGG", "TTGT", "TTTA", "TTTC", "TTTG", "TTTT"]
    if key > 255:
        return error("Key is too large (> 256)") 
    if key > 0:
        table = deque(defaultTable)
        table.rotate(-key)
        return table
    else:
        return defaultTable

def encryption(binary, table):
    i = 0
    j = 0
    dnaoutput = ""
    output = ""
    while i < len(binary):
        bitpair = binary[i:i+2]
        if bitpair == "00":
            dnaoutput += "A"
        elif bitpair == "01":
            dnaoutput += "T"
        elif bitpair == "10":
            dnaoutput += "G"
        elif bitpair == "11":
            dnaoutput += "C"
        j += 1
        i += 2
        if j == 4:
            output += '{0:08b}'.format(table.index(dnaoutput))
            j = 0
            dnaoutput = ""
    return output

def DNAencrypt(key, data):
    table = indexTable(key)
    overflow = ""
    if len(data)%8 != 0:
        overflow = data[-(len(data)%8):] 
        data = data[:(len(data)-(len(data)%8))] 
    start = datetime.now()
    encrypted = encryption(data, table)
    encrypted = encrypted + overflow
    return encrypted


def EncodedBinarytoDNA(cipher, table):
    i = 0
    output = ""
    while i < len(cipher):
        binarysequence = cipher[i:i+8]
        index = int(binarysequence, 2)
        output += table[index]
        i += 8
    return output

def dnaToBinary(binary):
    i = 0
    output = ""
    while i < len(binary):
        letter = binary[i]
        if letter == "A":
            output += "00"
        elif letter == "T":
            output += "01"
        elif letter == "G":
            output += "10"
        elif letter == "C":
            output += "11"
        i += 1
    return output

def DNAdecrypt(key, cipher):
    table = indexTable(key)
    overflow = ""
    if len(cipher)%8 != 0:
        overflow = cipher[-(len(cipher)%8):]
        cipher = cipher[:(len(cipher)-(len(cipher)%8))]
    start = datetime.now()
    dna = EncodedBinarytoDNA(cipher, table)
    start2 = datetime.now()
    decrypted = dnaToBinary(dna) + overflow
    return decrypted



# def key_generator(password):
#     simple_key = get_random_bytes(16)
#     # print(simple_key)
#     salt = simple_key
#     key = PBKDF2(password, salt, dkLen=32)
#     with open('./output/key_vv.bin', 'wb') as f:
#         password1 = bytes(password + "\n", "utf-8")
#         # print(password1)
#         f.write(password1)
#         f.write(key)
#     return key



def key_generator(password):
    simple_key = get_random_bytes(16)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    # Convert the key to an integer
    key_integer = int.from_bytes(key, byteorder='big') % 256
    with open('./output/key_vv.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        f.write(password1)
        f.write(key_integer.to_bytes((key_integer.bit_length() + 7) // 8, byteorder='big'))
    return key_integer



def setupTempDir():
    os.mkdir("output/temp/")



def cleanupTempFiles():
    shutil.rmtree("output/temp/")



def getImageDimensions(image_name):
    with Image.open(image_name) as img:
        if img.format != 'BMP':
            print(image_name + " must be .bmp format.")
        width, height = img.size
        return(width, height)
    


def stegoEncode(secret, cover, output):
    # Writing to encrypted image
    cover_image = Image.open(cover)
    cover_image.save(output) 
    
    output_image = Image.open(cover)
    # output_rgb = output_image.convert("RGB")
    width, height = output_image.size

    # pixels = output_rgb.load()
    
    data = np.asarray(output_image)

    #Embedding main payload at the beginning of the file
    i = 0
    finished = False
    for y in range(height):
        for x in range(width):
            r, g, b = data[y, x]

            #Red pixel
            if i < len(secret):
                # r_bit = bin(r)
                # r_new_final_bit = secret[i]
                new_bit_red_pixel = int(bin(r)[:-1]+str(secret[i]), 2)
                i += 1
            #Green pixel
            if i < len(secret):
                # g_bit = bin(g)
                # g_new_final_bit = secret[i]
                new_bit_green_pixel = int(bin(g)[:-1]+str(secret[i]), 2)
                i += 1
            #Blue pixel
            if i < len(secret):
                # b_bit = bin(b)
                # b_new_final_bit = secret[i]
                new_bit_blue_pixel = int(bin(b)[:-1]+str(secret[i]), 2)
                i += 1

            if i <= len(secret):
                data[y, x] = (new_bit_red_pixel, new_bit_green_pixel, new_bit_blue_pixel)
                if i >= len(secret):
                    i += 1
                    finished = True
                    break
        if finished:
            break



def encryptSecretImage(secret_image_name, key):
    with open(secret_image_name, "rb") as image:
            #Read image data in binary
            secret_image_bytes = bytes(image.read())
            image.close()
            secret_image_name_bytes = str.encode(secret_image_name)
            payload = secret_image_name_bytes + secret_image_bytes

    final_payload = payload
    raw_data = bin(int.from_bytes(final_payload, byteorder=sys.byteorder))[2:]
    cipher = DNAencrypt(key, raw_data)
    return(cipher)
        


# def encryptSecretImage(secret_image_name, key):
#     with open(secret_image_name, "rb") as image_file:
#         secret_image_bytes = image_file.read()

#     # Pad the secret image bytes to make its length a multiple of 16
#     padder = padding.PKCS7(128).padder()
#     padded_data = padder.update(secret_image_bytes)
#     padded_data += padder.finalize()

#     # Encrypt the padded data using AES in CBC mode
#     iv = os.urandom(16)  # Generate a random IV (Initialization Vector)
#     cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
#     encryptor = cipher.encryptor()
#     encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

#     # Concatenate the IV and encrypted data
#     ciphertext = iv + encrypted_data

#     return ciphertext, key



# def decryptSecretImage(cipher, key):
#     plaintext = DNAdecrypt(key, cipher)
    
#     def bitstring_to_bytes(s):
#         return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='little')

#     plaintext = bitstring_to_bytes(str(plaintext))
    

#     try:
#         filename = (plaintext[0:(plaintext.rfind(bytes('.bmp', 'utf-8')) + 4)]).decode('utf-8')
#         plaintext = plaintext[(plaintext.rfind(bytes('.bmp', 'utf-8')) + 4):]
#     except:
#         print("Decryption failed.")
#         return None


#     with open(filename, "wb") as write_image:
#         write_image.write(plaintext)
#         write_image.close()



def videoToImages(videoFile, type):
    valid_extensions = [".avi", ".mp4", ".mov", ".mkv"]  # Add other valid extensions here if needed
    if any(videoFile.endswith(ext) for ext in valid_extensions):
        start = datetime.now()
        vidcap = cv2.VideoCapture(videoFile)
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        success, image = vidcap.read()
        count = 0
        os.mkdir("output/temp/"+ type)

        while success:
            countString = str(count).zfill(10)
            # save frame as JPEG file
            cv2.imwrite("output/temp/" + type + "/%s.bmp" % countString, image)
            success, image = vidcap.read()
            count += 1
        return fps
    else:
        cleanupTempFiles()
        print("Incompatible video type. Supported formats: " + ", ".join(valid_extensions))



def encodeFrame(secretFrame, key):
    #Encrypting
    cipher = encryptSecretImage("output/temp/secret/" + secretFrame, key)

    # Writing to output image
    stegoEncode(cipher, "output/temp/cover/" + secretFrame, "temp/encoded/%s" % secretFrame)



def framesCompatabilityCheck(secretFrames, coverFrames):
    if len(secretFrames) > len(coverFrames):
        cleanupTempFiles()
        sys.exit("Secret video is longer than cover video.")
    
    try:
        secret_width, secret_height = getImageDimensions("output/temp/secret/" + secretFrames[0])
        secret_pixel_count = secret_width * secret_height
    except:
        print("First secret frame could not be read.")
        print(secretFrames[0])

    try:
        cover_width, cover_height = getImageDimensions("output/temp/cover/" + coverFrames[0])
        cover_pixel_count = cover_width * cover_height
    except:
        print("First cover frame could not be read.")
        print(coverFrames[0])
        
    return secret_pixel_count, cover_pixel_count



def stegoEncodeFrames(key):
    secretFrames = [img for img in os.listdir('output/temp/secret') if img.endswith(".bmp")]
    coverFrames = [img for img in os.listdir('output/temp/cover') if img.endswith(".bmp")]
    
    secret_pixel_count, cover_pixel_count = framesCompatabilityCheck(secretFrames, coverFrames)

    if ((cover_pixel_count / secret_pixel_count) > 8.2):
        if (len(secretFrames) <= len(coverFrames)):
            print("File compatability check complete!")
            
            os.mkdir("output/temp/encoded")
            
            threads = []
            
            print("Frame Encoding Progress:")
            
            pool = Pool(processes=10)
            for _ in tqdm.tqdm(pool.imap(partial(encodeFrame, key=key), secretFrames), total=len(secretFrames)):
                pass
                
        else:
            cleanupTempFiles()
            print("Video lengths incompatable. Cover video must be longer than the secret video.")
    else:
        cleanupTempFiles()
        print("Frame sizes incompatable. Cover video must be 8 times the resolution of the secret video.")



def imagesToVideo(video_name, type, fps):
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')

    image_folder = 'output/temp/' + type

    images = [img for img in os.listdir(image_folder) if img.endswith(".bmp")]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))


    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()


def main():
    while True:
        print("\n\t\tVIDEO STEGANOGRAPHY OPERATIONS") 
        print("1. Encode an Video")  
        # print("2. Decode an Image")  
        print("3. Exit")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1:
            password = input("Enter password for encryption: ")
            key = key_generator(password)
            setupTempDir()
            cover = 'resources/cover_test.avi'
            cover_fps = videoToImages(cover, "cover")
            secret =  'resources/secret_test.avi'
            videoToImages(secret, "secret")
            stegoEncodeFrames(key)
            output =  'output/output.avi'
            imagesToVideo(output, "encoded", cover_fps)
            cleanupTempFiles()

        # elif choice1 == 2:
        #     password = input("Enter password for decryption: ")
        #     # decoded_image_path = "./output/decoded.jpg"
        #     # decode_vid_data(a,password).save(decoded_image_path)
        #     decode_vid_image(a, password, img_shape)
        elif choice1 == 3:
            break
        else:
            print("Incorrect Choice")
        print("\n")

if __name__ == "__main__":
    main()     