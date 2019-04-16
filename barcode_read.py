import qi
import argparse
import sys
import time

ROBOT_IP = "192.168.1.105"
ROBOT_PORT = 9559

def barcode_reader(session):

    barcode_service = session.service("ALBarcodeReader")
    memory_service = session.service("ALMemory")

    barcode_service.subscribe("test_barcode")

    for range_counter in range(20):
        data = memory_service.getData("BarcodeReader/BarcodeDetected")
        if (len(data)):
            break
        time.sleep(2)
    return data

print ("Start")
session = qi.Session()

try:
    session.connect("tcp://" + ROBOT_IP + ":" + str(ROBOT_PORT))
except RuntimeError:
    print ("Can't connect to Naoqi at ip \"" + ROBOT_IP + "\" on port " + ROBOT_PORT + ".\n"
                                                                                          "Please check your script arguments. Run with -h option for help.")
    sys.exit(1)

identity = barcode_reader(session)
name = str(identity[0][0]).split(',')[0]
borrowedbooks = int(str(identity[0][0]).split(',')[2])
print (name)
print (borrowedbooks)

# text = barcode_reader(session)
# information = text[0][0]
# info_string = str(information)
# print(info_string.split(',')[0])
