from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def encrypt(key, password, msg):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphered_data = cipher.encrypt(pad(msg, AES.block_size))
    # print(ciphered_data)
    with open('encrypted.bin', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphered_data)
    return ciphered_data


def key_generator(password):
    simple_key = get_random_bytes(32)
    # print(simple_key)
    salt = simple_key
    key = PBKDF2(password, salt, dkLen=32)
    with open('key.bin', 'wb') as f:
        password1 = bytes(password + "\n", "utf-8")
        # print(password1)
        f.write(password1)
        f.write(key)
    return key


def decrypt(key, cypherText):
    with open('encrypted.bin', 'rb') as f:
        iv = f.read(16)
        cypherText = f.read()
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        og = unpad(cipher.decrypt(cypherText), AES.block_size)
    return og


def hide_msg_in_image(password, msg, path):
    # msg = bytes(message, "utf-8")
    image = Image.open(path)
    # print(image)
    # password = "1234"
    key = key_generator(password)
    print(key)
    encrypted_message = encrypt(key, password, msg)
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
    encoded_image.save('image_hidden.png')
    print("\n\nText embedded successfully!! Use image_hidden.png to retrieve the message.")


def retrieve_msg_from_image(password):
    path = input("Enter path of cover image: ")
    encoded_image = Image.open(path)
    binary_blocks = []
    for pixel in encoded_image.getdata():
        binary_block = format(pixel[2], '08b')
        binary_blocks.append(binary_block)
    encrypted_message = b''.join([int(block, 2).to_bytes(8, 'big') for block in binary_blocks])
    # print((encrypted_message))
    # password = "1234"
    # key = key_generator(password)
    with open('key.bin', 'rb') as f:
        data = f.read()
    contents = data.splitlines()
    # print(contents)
    password1 = contents[0]
    key = contents[1]
    # print(key)
    # print(str(password1, "utf-8"), "\n", password.strip())
    if str(password1, "utf-8") == password.strip():
        decrypted_message = decrypt(key, encrypted_message)
        message = decrypted_message.decode("utf-8")
        print("\n\n", message)
    else:
        print("Invalid Password!!")


if __name__ == '__main__':
    # password = input("Enter password for encryption: ")
    # msg = bytes(input("Enter message to be encrypted: "), "utf-8")
    print("\t\t\t\t\t#####  Welcome to text in image steganography tool  #####\n\n")
    while True:
        print("\n\n\t1. Hide message in image\n\t2. Retrieve message from image\n\t3. Exit")
        ch = int(input("\n\t\tChoose from below options: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            msg = bytes(input("Enter message to be encrypted: "), "utf-8")
            path = input("Enter path of cover image: ")
            hide_msg_in_image(password, msg, path)

        elif ch == 2:
            password = input("Enter password for decryption:")
            retrieve_msg_from_image(password)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")



    # cypherText = encrypt(key, password, msg)
    # # print(cypherText)
    # og = decrypt(key, cypherText)
    # print(str(og, "utf-8"))
    # message = "hey"
    # hide_msg_in_image(message)
    # retrieve_msg_from_image()