import os
import wave

# Function to hide a text message in an audio file


def hide_text_in_audio(audio_file, message, output_file):
    # Open the audio file for reading
    audio = wave.open(audio_file, 'rb')
    frames = audio.readframes(-1)

    # Convert the message to binary
    binary_message = ''.join(format(ord(char), '08b') for char in message)

    # Check if the audio file can hold the message
    if len(binary_message) > len(frames) * 8:
        raise Exception("Message too long to hide in this audio file")

    # Hide the message in the least significant bit of each audio sample
    encoded_frames = bytearray(frames)
    message_index = 0
    for i in range(len(encoded_frames)):
        if message_index < len(binary_message):
            encoded_frames[i] = (encoded_frames[i] & 0xFE) | int(
                binary_message[message_index])
            message_index += 1

    # Get the script's directory and create the output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = script_dir + "\output"
    output_path = os.path.join(script_dir, output_file)

    # Write the encoded frames to the output file
    with wave.open(output_path, 'wb') as output:
        output.setparams(audio.getparams())
        output.writeframes(encoded_frames)

    print("Message hidden successfully! Output file saved as", output_path)


# Function to extract a hidden text message from an audio file


def extract_text_from_audio(encoded_audio_file):
    audio = wave.open(encoded_audio_file, 'rb')
    frames = audio.readframes(-1)

    # Initialize variables
    binary_message = ""
    message = ""
    consecutive_zeros = 0

    for frame in frames:
        # Extract the least significant bit
        bit = frame & 1
        binary_message += str(bit)

        # Check for consecutive zeros (end of message marker)
        if bit == 0:
            consecutive_zeros += 1
        else:
            consecutive_zeros = 0

        # If we have eight consecutive zeros, it's the end of the message
        if consecutive_zeros == 8:
            break

    # Remove the trailing zeros from the binary message
    binary_message = binary_message[:-8]

    # Convert the binary message to text
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i + 8]
        message += chr(int(byte, 2))

    print("Extracted Message:", message)  # Print the extracted message as text

# Main function


def caller():
    # choice = input("Enter 1 for encryption or 2 for decryption: ")

    # if choice == '1':
    #     audio_file = input("Enter the path of the audio file: ")
    #     message = input("Enter the text message to hide: ")
    #     output_file = input(
    #         "Enter the output file name (e.g., encoded_audio.wav): ")
    #     hide_text_in_audio(audio_file, message, output_file)
    # elif choice == '2':
    #     encoded_audio_file = input(
    #         "Enter the path of the encoded audio file: ")
    #     extracted_message = extract_text_from_audio(encoded_audio_file)
        
    # else:
    #     print("Invalid choice. Please enter 1 for encryption or 2 for decryption.")


    while True:
        print("\n\n\t1. Hide text in audio\n\t2. Retrieve text from audio\n\t3. Exit")
        ch = int(input("\n\t\tChoose from below options: \n"))

        if ch == 1:
            audio_file= input("Enter path of Audio: ")
            message = input("Enter the text message to hide: ")
            output_file = input("Enter the output file name (e.g., encoded_audio.wav): ")
            hide_text_in_audio(audio_file, message, output_file) 

        elif ch == 2:
            encoded_audio_file = input("Enter the path of the encoded audio file: ")
            extract_text_from_audio(encoded_audio_file)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")


