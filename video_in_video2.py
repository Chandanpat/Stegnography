import cv2
import os
import shutil
import sys
from datetime import datetime
import tqdm
from PIL import Image
import numpy as np

def setupTempDir():
    os.makedirs("output/temp/", exist_ok=True)

def cleanupTempFiles():
    shutil.rmtree("output/temp/", ignore_errors=True)

def videoToImages(videoFile, type):
    valid_extensions = [".avi", ".mp4", ".mov", ".mkv"]  
    if any(videoFile.endswith(ext) for ext in valid_extensions):
        os.makedirs("output/temp/"+ type, exist_ok=True)
        vidcap = cv2.VideoCapture(videoFile)
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        success, image = vidcap.read()
        count = 0

        while success:
            countString = str(count).zfill(10)
            cv2.imwrite(f"output/temp/{type}/{countString}.png", image)
            success, image = vidcap.read()
            count += 1
        return fps
    else:
        cleanupTempFiles()
        print("Incompatible video type. Supported formats: " + ", ".join(valid_extensions))

def embedVideoLSB(secretFrame, coverFrame):
    secret_image = Image.open(f"output/temp/secret/{secretFrame}")
    cover_image = Image.open(f"output/temp/cover/{coverFrame}")

    # Resize the secret video frame to match the dimensions of the cover video frame
    secret_image = secret_image.resize(cover_image.size)

    secret_data = np.array(secret_image)
    cover_data = np.array(cover_image)

    # Embed secret video data into LSB of cover video data
    cover_data[:, :, 0] = (cover_data[:, :, 0] & 0xFE) | ((secret_data[:, :, 0] >> 7) & 1)
    cover_data[:, :, 1] = (cover_data[:, :, 1] & 0xFE) | ((secret_data[:, :, 1] >> 7) & 1)
    cover_data[:, :, 2] = (cover_data[:, :, 2] & 0xFE) | ((secret_data[:, :, 2] >> 7) & 1)

    # Create the directory if it doesn't exist
    os.makedirs("output/temp/encoded/", exist_ok=True)

    merged_image = Image.fromarray(cover_data)
    merged_image.save(f"output/temp/encoded/{coverFrame}")



def stegoEncodeFrames():
    secretFrames = sorted([img for img in os.listdir('output/temp/secret') if img.endswith(".png")])
    coverFrames = sorted([img for img in os.listdir('output/temp/cover') if img.endswith(".png")])

    print("Frame Encoding Progress:")
    for secretFrame, coverFrame in tqdm.tqdm(zip(secretFrames, coverFrames), total=len(secretFrames)):
        embedVideoLSB(secretFrame, coverFrame)

def imagesToVideo(video_name, type, fps):
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    image_folder = f'output/temp/{type}'
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, _ = frame.shape
    video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))
    cv2.destroyAllWindows()
    video.release()

def extractFramesFromEncodedVideo(videoFile):
    os.makedirs("output/temp/extracted_frames/", exist_ok=True)
    vidcap = cv2.VideoCapture(videoFile)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    success, image = vidcap.read()
    count = 0

    while success:
        countString = str(count).zfill(10)
        cv2.imwrite(f"output/temp/extracted_frames/{countString}.png", image)  # Save frames as PNG
        success, image = vidcap.read()
        count += 1
    return fps

def extractSecretDataFromFrames():
    extractedFrames = sorted([img for img in os.listdir('output/temp/extracted_frames/') if img.endswith(".png")])  # Look for PNG files

    secret_data = []
    for frame in extractedFrames:
        frame_image = Image.open(f"output/temp/extracted_frames/{frame}")
        frame_data = np.array(frame_image)

        # Extract the LSBs from each channel to retrieve the secret data
        secret_channel_0 = (frame_data[:, :, 0] & 1) << 7
        secret_channel_1 = (frame_data[:, :, 1] & 1) << 7
        secret_channel_2 = (frame_data[:, :, 2] & 1) << 7
        
        # Combine the extracted LSBs from each channel
        secret_data.extend([secret_channel_0, secret_channel_1, secret_channel_2])

    return np.array(secret_data)


def reconstructSecretVideo(secret_data, fps):
    os.makedirs("output/extracted_secret_video/", exist_ok=True)
    secret_frames = []
    for i in range(0, len(secret_data), 3):
        merged_data = np.zeros((secret_data[i].shape[0], secret_data[i].shape[1], 3), dtype=np.uint8)
        merged_data[:, :, 0] = (merged_data[:, :, 0] & 0xFE) | (secret_data[i] >> 7)
        merged_data[:, :, 1] = (merged_data[:, :, 1] & 0xFE) | (secret_data[i + 1] >> 7)
        merged_data[:, :, 2] = (merged_data[:, :, 2] & 0xFE) | (secret_data[i + 2] >> 7)
        secret_frames.append(merged_data)

    for idx, frame_data in enumerate(secret_frames):
        frame_image = Image.fromarray(frame_data)
        frame_image.save(f"output/extracted_secret_video/frame_{idx}.png")

    imagesToVideo("output/extracted_secret_video/extracted_secret_video.avi", "encoded", fps)


def main():
    while True:
        print("\n\t\tVIDEO STEGANOGRAPHY OPERATIONS")
        print("1. Embed Secret Video in Cover Video")
        print("2. Extract Secret Video from Cover Video")
        print("3. Exit")
        choice1 = int(input("Enter the Choice: "))
        if choice1 == 1:
            setupTempDir()
            cover = 'resources/cover_test.avi'
            cover_fps = videoToImages(cover, "cover")
            secret = 'resources/secret_test.avi'
            videoToImages(secret, "secret")
            stegoEncodeFrames()
            output = 'output/output.avi'
            imagesToVideo(output, "encoded", cover_fps)
            # cleanupTempFiles()
        elif choice1 == 2:
            encoded_video = 'output/output.avi'
            encoded_fps = extractFramesFromEncodedVideo(encoded_video)
            secret_data = extractSecretDataFromFrames()
            reconstructSecretVideo(secret_data, encoded_fps)
            # cleanupTempFiles()
        elif choice1 == 3:
            break
        else:
            print("Incorrect Choice")

if __name__ == "__main__":
    main()

