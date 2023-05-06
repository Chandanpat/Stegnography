import numpy as np
from PIL import Image
import wave
import math

# Load image
img = Image.open("image_file3.png")
img = np.array(img)

# Load audio
with wave.open("audio_file.wav", "rb") as audio:
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
img_flat = img.flatten()
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
img_steg.save("image_steg.png")

# Extract audio from steganographic image
img_flat = img.flatten()
audio_bin = ""
for i in range(len(prn_seq)):
    audio_bin += str(img_flat[i] & 1)
audio_samples = np.zeros(N, dtype=np.float32)
for i in range(N):
    audio_samples[i] = (2.0 * (float(int(audio_bin[i])) - 0.5) -
                        alpha * math.sin(2.0 * math.pi * f0 * i / fs)) / alpha
audio_samples = (audio_samples * 32767.0).astype(np.int16)
with wave.open("audio_steg.wav", "wb") as audio:
    audio.setnchannels(1)
    audio.setsampwidth(2)
    audio.setframerate(44100)
    audio.writeframes(audio_samples.tobytes())
