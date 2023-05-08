import TextInText as TinT
import text_in_image as TinI
import LSB_Img_in_Img as IinI
import audimg as AinI


print("\n\n\t\t\t\t\t#####  Welcome to Multimedia Steganography Tool  #####\n\n")
while True:
   print("\n\n\t1. Text in Text Steganography\n\t2. Text in Image Steganography\n\t3. Image in Image Steganography\n\t4. Audio in Image Steganography\n\t5. Exit")
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
        print("\n\nExiting.....")
        break
   
   else:
        print("\n\nInvalid Choice!!")