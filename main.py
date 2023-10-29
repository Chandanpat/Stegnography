import TextInText as TinT
import text_in_image as TinI
import LSB_Img_in_Img as IinI
import txtinaudio as TinA
import audimg as AinI
import text_in_video as TinV


print("\n\n\t\t\t\t\t#####  Welcome to Multimedia Steganography Tool  #####\n\n")
while True:
   print("\n\n\t1. Text in Text Steganography\n\t2. Text in Image Steganography\n\t3. Image in Image Steganography\n\t4. Audio in Image Steganography\n\t5. Text in Audio Steganography\n\t6. Text in Video Steganography\n\t7. Exit")
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
        print("\n\nExiting.....")
        break
   else:
        print("\n\nInvalid Choice!!")