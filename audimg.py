import numpy as np
from PIL import Image
import wave
import math

def encode(audio_path,image_path):
# Load image
    img = Image.open(image_path)
    img = np.array(img)

# Load audio
    with wave.open(audio_path, "rb") as audio:
        nframes = audio.getnframes()
        audio_frames = audio.readframes(nframes)
    audio_samples = np.frombuffer(audio_frames, dtype=np.int16)
    audio_samples = audio_samples.astype(np.float32) / 32767.0

# Parameters for Spread Spectrum Steganography
    alpha = 0.5
    f0 = 4000.0
    fs = 44100.0
    N = len(audio_samples)

# Generate pseudorandom sequence
    np.random.seed(0)
    prn_seq = np.random.randint(2, size=N)

# Embed audio into image
    img_flat = np.asarray(img).ravel()
    audio_bin = "".join(["{0:b}".format(int(x * 32767.0 + 32768))
                        for x in audio_samples])
    audio_bin = audio_bin.zfill(len(prn_seq))
    audio_bin = audio_bin[:len(prn_seq)]
    for i in range(len(prn_seq)):
        img_flat[i] = (img_flat[i] & ~1) | (prn_seq[i] ^ int(
            alpha * math.sin(2.0 * math.pi * f0 * i / fs)) ^ int(audio_bin[i]))
    img = img_flat.reshape(img.shape)

# Save steganographic image
    img_steg = Image.fromarray(img)
    img_steg.save("./output/image_steg.png")
    print("\n\naudio embedded successfully!! Use image_steg.png to retrieve the message.")
    


def decode(encryted_image):
    audio_path = "./resources/audio_file.wav"
    with wave.open(audio_path, "rb") as audio:
        nframes = audio.getnframes()
        audio_frames = audio.readframes(nframes)
    audio_samples = np.frombuffer(audio_frames, dtype=np.int16)
    audio_samples = audio_samples.astype(np.float32) / 32767.0
    img = Image.open(encryted_image)


    alpha = 0.5
    f0 = 4000.0
    fs = 44100.0
    N = len(audio_samples)
    prn_seq = np.random.randint(2, size=N)


# Extract audio from steganographic image
    img_flat = np.asarray(img).ravel()
    audio_bin = ""
    for i in range(len(prn_seq)):
        audio_bin += str(img_flat[i] & 1)
    audio_samples = np.zeros(N, dtype=np.float32)
    for i in range(N):
        audio_samples[i] = (2.0 * (float(int(audio_bin[i])) - 0.5) -
                            alpha * math.sin(2.0 * math.pi * f0 * i / fs)) / alpha
    audio_samples = (audio_samples * 32767.0).astype(np.int16)
    with wave.open("./output/audio_steg.wav", "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(44100)
        audio.writeframes(audio_samples.tobytes())



def caller():
    
    while True:
        print("\n\n\t1. Hide audio in image\n\t2. Retrieve audio from image\n\t3. Exit")
        ch = int(input("\n\t\tChoose from below options: \n"))

        if ch == 1:
            audio_path= input("Enter path of Audio: ")
            image_path= input("Enter path of Image: ")
            encode(audio_path,image_path)
            

        elif ch == 2:
            encryted_image=input("Enter path of Encrypted image: ")
            decode(encryted_image)

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")
