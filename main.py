import text_in_text as TinT
import text_in_image as TinI
import image_in_image as IinI
import text_in_audio as TinA
# import audimg as AinI
import audio_in_image as AinI
import text_in_video as TinV
import image_in_video as IinV


print("\n\n\t\t\t\t\t#####  Welcome to Multimedia Steganography Tool  #####\n\n")
while True:
   print("\n\n\t1. Text in Text Steganography\n\t2. Text in Image Steganography\n\t3. Image in Image Steganography\n\t4. Audio in Image Steganography\n\t5. Text in Audio Steganography\n\t6. Text in Video Steganography\n\t7. Image in Video Steganography\n\t8. Exit")
   ch = int(input("\n\t\tChoose from below options: \n"))

   if ch == 1:
        TinT.caller()

   elif ch == 2:
        TinI.caller()

   elif ch == 3:
        IinI.caller()

   elif ch == 4:
        AinI.caller()

   elif ch == 5:
        TinA.caller()

   elif ch == 6:
        TinV.caller()

   elif ch == 7:
        IinV.caller()
   
   elif ch == 8:
        print("\n\nExiting.....")
        break
   else:
        print("\n\nInvalid Choice!!")