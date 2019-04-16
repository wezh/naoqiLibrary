
# -*- encoding: UTF-8 -*-

"""Example: Shows how images can be accessed through ALVideoDevice"""

import qi
import argparse
import sys
import time


def main(session):
    """
    This is just an example script that shows how images can be accessed
    through ALVideoDevice in Python.
    Nothing interesting is done with the images in this example.
    """
    # Get the services ALBarcodeReader and ALMemory.

    barcode_service = session.service("ALBarcodeReader")
    memory_service = session.service("ALMemory")

    barcode_service.subscribe("test_barcode")

    # Query last data from ALMemory twenty times
    for range_counter in range(20):
        data = memory_service.getData("BarcodeReader/BarcodeDetected")
        print data
        time.sleep(1)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--ip", type=str, default="192.168.1.105",
    #                     help="Robot IP address. On robot or Local Naoqi: use '192.168.1.105'.")
    # parser.add_argument("--port", type=int, default=9559,
    #                     help="Naoqi port number")

    # args = parser.parse_args()
    session = qi.Session()
    print("session ok")
    try:
        session.connect("tcp://" + "192.168.1.105" + ":" + str(9559))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + "192.168.8.105" + "\" on port " + str(9559) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)