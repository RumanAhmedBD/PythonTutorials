'''

from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
reader = SimpleMFRC522()

while 1:
    try:
        print("Place your RFID tag near the reader...")
        id, text = reader.read()
        print(f"ID: {id}")
        #print(f"Text: {text}")
    finally:
        GPIO.cleanup()


'''

from mfrc522 import MFRC522
import RPi.GPIO as GPIO
import time

reader = MFRC522()

try:
    print("Place your RFID tag near the reader...")
    while True:
        status, TagType = reader.MFRC522_Request(reader.PICC_REQIDL)

        if status == reader.MI_OK:
            print("Card detected")

            status, uid = reader.MFRC522_Anticoll()
            if status == reader.MI_OK:
                #card_uid = "{:02X}{:02X}{:02X}{:02X}".format(uid[0], uid[1], uid[2], uid[3])
                #print(f"UID: {card_uid}")
                print(f"UID: {uid}")
                time.sleep(1)  # debounce delay

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    GPIO.cleanup()
