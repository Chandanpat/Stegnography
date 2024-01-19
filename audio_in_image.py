import ffmpy
import soundfile as sf
import numpy as np
import cv2
import cv2
import numpy as np
import soundfile as sf



def mp3towav(src,dest):
    ff = ffmpy.FFmpeg(
        inputs={src: None},
        outputs={dest: None})
    ff.run()




def wavtomp3(src,dest):
    ff = ffmpy.FFmpeg(
        inputs={src: None},
        outputs={dest: None})
    ff.run()




# def openmp3(filename):
#     with open(filename,'rb') as f:

#        while f.readable():
#             print (f.read(1))




def audiotoimage(audio_path, image_path):

    data, samplerate = sf.read(audio_path,dtype='int16')
    # print(len(data))

    # print(data[120000])

    # print(samplerate)

    npdata =  np.array(data)
    npdatat  = npdata.transpose()

    channel1 = npdatat[0]
    channel2 = npdatat[1]

    def paddingzeroesattheend(array,no):
        arr=[]
        i = 0
        while(i<=no):
            arr.append(0)
            i=i+1

        array = np.append(array,arr)
        return array



    length =  len(channel1)
    square = length**(0.5)

    if (square> int(square)):
        square = int(square) + 1

    # print(square)



    channel1 = paddingzeroesattheend(channel1,((square*square)-len(channel1)-1))
    channel2 = paddingzeroesattheend(channel2,((square*square)-len(channel2)-1))

    channel1 = np.array(channel1)
    channel2 = np.array(channel2)

    channel1 = channel1 + 32768
    channel2 = channel2 + 32768

    channel1front = channel1 / 256
    channel1end = channel1front - channel1front.astype(int)
    channel1end = channel1end*256

    channel1front = channel1front.astype(int)
    channel1end = channel1end.astype(int)

    channel2front = channel2 / 256
    channel2end = channel2front - channel2front.astype(int)
    channel2end = channel2end*256

    channel2front = channel2front.astype(int)
    channel2end = channel2end.astype(int)




    d2channel1front  = np.reshape(channel1front,(square,square))
    d2channel1end  = np.reshape(channel1end,(square,square))
    d2channel2front  = np.reshape(channel2front,(square,square))
    d2channel2end  = np.reshape(channel2end,(square,square))

    allchannel = [d2channel1front,d2channel2front,d2channel1end,d2channel2end]

    allchannel = np.array(allchannel)


    allchannel = np.transpose(allchannel)
    # print(allchannel)
    # print("Type = ",type(allchannel))

    # cv2.imwrite(image_path, allchannel,[cv2.IMWRITE_PNG_COMPRESSION,9])
    encoded_img = input("Enter name of the stego file with extension: ")
    cv2.imwrite("./output/"+encoded_img, allchannel,[cv2.IMWRITE_PNG_COMPRESSION,9])

    print("\n\nAudio embedded successfully!! Check " + encoded_img +" and use it for retrieving original audio.")

    # print("done2")



def imagetoaudio(filename,outputdes):

    img = cv2.imread(filename,cv2.IMREAD_UNCHANGED)


    allchannel  =  np.array(img)

    allchannel = np.transpose(allchannel)



    d2channel1front  = np.array(allchannel[0])

    d2channel2front  = np.array(allchannel[1])

    d2channel1end  = np.array(allchannel[2])

    d2channel2end  = np.array(allchannel[3])

    channel1front  = np.reshape(d2channel1front,(1,-1))
    channel1front  = np.array(channel1front[0])
    channel1end  = np.reshape(d2channel1end,(1,-1))
    channel1end  = np.array(channel1end[0])
    channel2front  = np.reshape(d2channel2front,(1,-1))
    channel2front  = np.array(channel2front[0])
    channel2end  = np.reshape(d2channel2end,(1,-1))
    channel2end  = np.array(channel2end[0])

    channel1 = (channel1front*256 + channel1end)
    channel2 = (channel2front*256 + channel2end)

    channel1 = channel1.astype(int)
    channel2 = channel2.astype(int)

    channel1 = channel1-32768
    channel2 = channel2-32768

    data = [channel1,channel2]

    data = np.array(data)
    data = np.transpose(data)

    data = data[0:14467107]


    npdata = data.astype('int16')

    sf.write(outputdes,npdata, 44100)




def caller():
    while True:
        print("\n\n\t1. Hide audio in image\n\t2. Retrieve audio from image\n\t3. Exit")
        ch = int(input("\n\t\tEnter your choice: \n"))

        if ch == 1:
            # password = input("Enter password for encryption: ")
            audio_path = input("Enter path of audio to be hidden: ")
            image_path = input("Enter path of cover image: ")
            audiotoimage(audio_path, image_path)

        elif ch == 2:
            # password = input("Enter password for decryption:")
            image_path = input("Enter path of stego image: ")
            audio_path = "./output/decodedAudio.wav"
            imagetoaudio(image_path,audio_path)
            print("\n\nAudio extracted successfully!! Check decodedAudio.wav")

        elif ch == 3:
            print("\n\nExiting.....")
            break

        else:
            print("\n\nInvalid Choice!!")


