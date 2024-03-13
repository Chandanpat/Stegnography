from PIL import Image
from essentials import *



def hide_msg_in_image(password,):
    msg = bytes(input("Enter message to be encrypted: "), "utf-8")
    path = input("Enter path of cover image: ")
    # msg = bytes(message, "utf-8")
    image = Image.open(path)
    # print(image)
    # password = "1234"
    key = key_generator(password,'ti')
    print(key)
    encrypted_message = encrypt(key, msg, 'ti')
    message_blocks = [encrypted_message[i:i + 8] for i in range(0, len(encrypted_message), 8)]
    # print(message_blocks)
    binary_blocks = [format(int.from_bytes(block, 'big'), '064b') for block in message_blocks]
    # print(binary_blocks)
    pixels = list(image.getdata())
    encoded_pixels = []
    for i, pixel in enumerate(pixels):
        if i < len(binary_blocks):
            encoded_pixel = (pixel[0], pixel[1], pixel[2] | int(binary_blocks[i][-1]))
        else:
            encoded_pixel = pixel
        encoded_pixels.append(encoded_pixel)
    # print(encoded_pixel)
    encoded_image = Image.new(image.mode, image.size)
    encoded_image.putdata(encoded_pixels)
    file_name = input("Enter the name of stego file to be generated: ")
    encoded_image.save('./output/'+ file_name)
    print("\n\n\nText embedded successfully!! Stego file saved as: ./output/",file_name)



def retrieve_msg_from_image(password):
    key,check = checkPass(password,'ti')
    if check == True:
        path = input("Enter path of cover image: ")
        encoded_image = Image.open(path)
        binary_blocks = []
        for pixel in encoded_image.getdata():
            binary_block = format(pixel[2], '08b')
            binary_blocks.append(binary_block)
        encrypted_message = b''.join([int(block, 2).to_bytes(8, 'big') for block in binary_blocks])
        decrypted_message = decrypt(key, encrypted_message,'ti')
        message = decrypted_message.decode("utf-8")
        print("\n\n\nMessage after decoding from the stego file:- ", message)
    else:
        print("Invalid Password!!")



def caller():
    # password = input("Enter password for encryption: ")
    # msg = bytes(input("Enter message to be encrypted: "), "utf-8")
    # print("\t\t\t\t\t#####  Welcome to text in image steganography tool  #####\n\n")
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
            password = input("Enter password for decryption:")
            retrieve_msg_from_image(password)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")