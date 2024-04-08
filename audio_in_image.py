from PIL import Image
from PIL import Image
import wave
from essentials import *



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



def encode(password):
    audio_to_hide_path = input("Enter path of audio to be hidden: ")
    # audio_to_hide_path = "./resources/audio_file.wav"
    image_to_hide_in_path = input("Enter path of cover image: ")
    # image_to_hide_in_path = "./resources/image.jpg"
    encoded_image_path = "./output/"+input("Enter the name of stego file to be generated: ")
    # encoded_image_path = "./output/image_output.jpg"
    n_bits = 1
    image_to_hide_in = Image.open(image_to_hide_in_path)
    width, height = image_to_hide_in.size
    hide_in_image = image_to_hide_in.load()

    # Open the secret audio file for reading
    with wave.open(audio_to_hide_path, 'rb') as secret_audio_file:
        secret_frames = secret_audio_file.readframes(-1)

    # Encrypt the secret audio data
    key = key_generator(password,'ai')
    encrypted_audio = encrypt(key, secret_frames, 'ai')

    data = []

    a = 0
    b = 0

    # Use an iterator for the encrypted image bytes
    encrypted_iterator = iter(encrypted_audio)
    for y in range(height):
        for x in range(width):
            try:
                # Extract bytes from the encrypted audio for each channel
                r_byte = next(encrypted_iterator)
                g_byte = next(encrypted_iterator)
                b_byte = next(encrypted_iterator)
    
                # Extract the n most significant bits
                r_hide_pixel = get_n_most_significant_bits(r_byte, n_bits)
                g_hide_pixel = get_n_most_significant_bits(g_byte, n_bits)
                b_hide_pixel = get_n_most_significant_bits(b_byte, n_bits)
    
                # Remove the least n significant bits from the cover image
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



def decode(password):
    key,check = checkPass(password,'ai')
    if check == True:
        encoded_image_path = input("Enter the path of Stego image: ")
        # encoded_image_path = "./output/image_output.jpg"
        decoded_audio_path = "./output/"+input("Enter the name of output file to be generated: ")
        # decoded_audio_path = "./output/output_audio.wav"
        n_bits = 1

        # Open the stego image for decoding
        image_to_decode = Image.open(encoded_image_path)
        width, height = image_to_decode.size
        encoded_image = image_to_decode.load()

        # List to store extracted audio frames
        extracted_audio_frames = bytearray()

        # Iterate through each pixel in the image
        for y in range(height):
            for x in range(width):
                r_encoded, g_encoded, b_encoded = encoded_image[x, y]

                # Extract the least significant bits
                r_encoded = get_n_least_significant_bits(r_encoded, n_bits)
                g_encoded = get_n_least_significant_bits(g_encoded, n_bits)
                b_encoded = get_n_least_significant_bits(b_encoded, n_bits)

                # Reconstruct the original byte
                original_byte = r_encoded | g_encoded | b_encoded

                # Append the reconstructed byte to the extracted audio frames
                extracted_audio_frames.append(original_byte)

        decrypted_audio = decrypt(key, extracted_audio_frames,"ai")

        # Write the decrypted audio to the output file
        with wave.open(decoded_audio_path, 'wb') as output_audio_file:
            output_audio_file.setnchannels(2)  # Specify the number of channels
            output_audio_file.setframerate(22050)
            output_audio_file.setsampwidth(2)  # Set sample width to 2 bytes for 16-bit audio
            output_audio_file.writeframes(decrypted_audio)

        print("\n\n\nAudio extracted successfully! Output file saved as:", decoded_audio_path)
    else:
        print("Invalid Password!!")



def caller():
    while True:
        print("\n\t\tAUDIO IN IMAGE STEGANOGRAPHY OPERATIONS") 
        print("1. Encode Audio in Image")  
        print("2. Decode Audio from Image")  
        print("3. Exit") 
        ch = int(input("\n\t\t Enter your choice: \n"))

        if ch == 1:
            password = input("Enter password for encryption: ")
            encode(password)

        elif ch == 2:
            password = input("Enter password for decryption: ")
            decode(password)
            
        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")
