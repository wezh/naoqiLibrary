import qi
import argparse
import sys
import time

ROBOT_IP = "192.168.1.105"

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

parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, default="192.168.1.105",
                        help="Robot IP address. On robot or Local Naoqi: use '192.168.1.105'.")

parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
args = parser.parse_args()
session = qi.Session()
try:
    session.connect("tcp://" + args.ip + ":" + str(args.port))
except  RuntimeError:
    print ("Can't connect to Naoqi at ip \"" + ROBOT_IP + "\" on port " + str(args.port) + ".\n"
                                                                                          "Please check your script arguments. Run with -h option for help.")
    sys.exit(1)

text = barcode_reader(session)
information = text[0][0]
info_string = str(information)
print(info_string.split(',')[0])
