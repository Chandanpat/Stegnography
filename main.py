import text_in_text as TinT

import text_in_image as TinI
import image_in_image as IinI
import audio_in_image as AinI

import text_in_audio as TinA
import image_in_audio as IinA
import audio_in_audio as AinA

import text_in_video as TinV
import image_in_video as IinV
import audio_in_video as AinV

def print_header():
    print("\n")
    print("╔" + "═" * 80 + "╗")
    print("║" + " " * 26 + "MULTIMEDIA STEGANOGRAPHY TOOL" + " " * 25 + "║")
    print("╚" + "═" * 80 + "╝")

def print_options():
    print("\n\nOptions:")
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║ 1. Text in Text Steganography                                                  ║")
    print("║                                                                                ║")
    print("║ 2. Text in Image Steganography                                                 ║")
    print("║ 3. Image in Image Steganography                                                ║")
    print("║ 4. Audio in Image Steganography                                                ║")
    print("║                                                                                ║")
    print("║ 5. Text in Audio Steganography                                                 ║")
    print("║ 6. Image in Audio Steganography                                                ║")
    print("║ 7. Audio in Audio Steganography                                                ║")
    print("║                                                                                ║")
    print("║ 8. Text in Video Steganography                                                 ║")
    print("║ 9. Image in Video Steganography                                                ║")
    print("║ 10. Audio in Video Steganography                                               ║")
    print("║                                                                                ║")
    print("║ 11. Exit                                                                       ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")

def main():
    print_header()
    while True:
        print_options()
        ch = int(input("\n\t\tChoose from above options: "))
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
            IinA.caller()
        elif ch == 7:
            AinA.caller()
        elif ch == 8:
            TinV.caller()
        elif ch == 9:
            IinV.caller()
        elif ch == 10:
            AinV.caller()
        elif ch == 11:
            print("\n\nExiting.....")
            break
        else:
            print("\n\nInvalid Choice!!")

if __name__ == "__main__":
    main()          