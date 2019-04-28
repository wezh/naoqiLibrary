from __future__ import print_function

import argparse
import os
import io
import datetime
import time
import sys

# Import Folder looping API
import glob

# Import SFTP Process API
import paramiko

# Import Picture Procressing API
from coverdescriptor import CoverDescriptor
from covermatcher import CoverMatcher
import csv
import cv2

# Import NAOqi proxy API
from naoqi import *
import qi

# import google speech environment
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# set Robot IP and PORT
global tts, audio, record, audioplayer, photo
ap = argparse.ArgumentParser()
user = "nao"
passwd = "nimdA"
ROBOT_IP = "192.168.1.105"
ROBOT_PORT = 9559

checklist_borrow = ("borrow", "take")
checklist_return = ("return", "back")
checklist_end = ("no", "not")

# List of Photo and Audio Path and File in NAO Robot
nao_recordingPath = "/home/nao/Library/recordingTemp/"
nao_photoPath = "/home/nao/Library/queryTemp/"
# nao_recordingFile = "/home/nao/recording/recording.wav"
nao_recordingFile = "/home/nao/Library/recordingTemp/recording.wav"

# List of Photo and Audio File in local computer
local_recordingPath = "./recording/"
local_recordingFile = "./recording/recording.wav"
local_photoPath = "./querys/"


# Speech to Text Method By Google Speech API
def SpeechTransferToText(speech_file):
    # connect to google speech service
    # Instantiates a client
    client = speech.SpeechClient()

    # Loads the audio into memory
    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='en-US')

    # Detects speech in the audio file
    response = client.recognize(config, audio)

    for result in response.results:
        text = "{}".format(result.alternatives[0].transcript)
        print("User: " + text)
        return text



# Transfer audio or query files from NAO Robot
def TransferFile(ROBOT_IP, user, passwd, remoteFilePath, localFilePath):
    try:
        t = paramiko.Transport((ROBOT_IP, 22))
        t.connect(username=user, password=passwd)
        sftp = paramiko.SFTPClient.from_transport(t)
        files = sftp.listdir(remoteFilePath)
        for f in files:
            print('##############################################')
            print('Beginning to download audio file from %s %s' % (ROBOT_IP, datetime.datetime.now()))
            print('Downloading audio file:', os.path.join(remoteFilePath, f))
            sftp.get(os.path.join(remoteFilePath, f), os.path.join(localFilePath, f))
            print('Download audio file success %s' % datetime.datetime.now())
            print('##############################################')
        t.close()
    except Exception:
        print("connect error!")

# Read Bar Code
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

# Record user speaking from NAO
def recordAudioFromNao():
    record.stopMicrophonesRecording()
    # Start Recording from NAO AUDIO DEVICE
    print('#########################################################')
    print('start recording.')
    tts.say('start recording')
    # nao_recordingFile = '/home/nao/Library/recordingTemp/recording.wav'
    record.startMicrophonesRecording('/home/nao/Library/recordingTemp/recording.wav', 'wav', 16000, (0, 0, 1, 0))
    # record.startMicrophonesRecording(nao_recordingFile, 'wav', 16000, (0, 0, 1, 0))
    time.sleep(4)
    record.stopMicrophonesRecording()
    print('stop recording.')
    tts.say("stop recording.")
    print('#########################################################')

# Capture Book Cover
def photoCapture():
    print ("Please put the book cover in front of my eyes.")
    tts.say("Please put the book cover in front of my eyes.")
    time.sleep(2)
    print ("Capturing picture...")
    tts.say("Capturing picture...")
    time.sleep(2)
    photo.setResolution(2)
    photo.setPictureFormat("png")
    photo.takePictures(1, "/home/nao/Library/queryTemp/", "query")
    print ("Finished")
    tts.say("Finished")


def checkBooks(numberOfBorrowedBooks):
    if numberOfBorrowedBooks > 0:
        return True
    else:
        return False


# Conncted to NAO ROBOT
session = qi.Session()

ap.add_argument("-s", "--sift", type=int, default=0, help="whether or not SIFT should be used")
args = vars(ap.parse_args())

try:
    audio = ALProxy("ALAudioDevice", ROBOT_IP, ROBOT_PORT)
    record = ALProxy("ALAudioRecorder", ROBOT_IP, ROBOT_PORT)
    audioplayer = ALProxy("ALAudioPlayer", ROBOT_IP, ROBOT_PORT)
    photo = ALProxy("ALPhotoCapture", ROBOT_IP, ROBOT_PORT)
    tts = ALProxy("ALTextToSpeech", ROBOT_IP, ROBOT_PORT)
    asr = ALProxy("ALSpeechRecognition", ROBOT_IP, ROBOT_PORT)
    memory = ALProxy("ALMemory", ROBOT_IP, ROBOT_PORT)
    barcode = ALProxy("ALBarcodeReader", ROBOT_IP, ROBOT_PORT)
    broker = ALBroker("pythonBroker", "0.0.0.0", 0, ROBOT_IP, ROBOT_PORT)
except Exception, e:
    print(str(e))
    exit(1)

try:
    session.connect("tcp://" + ROBOT_IP + ":" + str(ROBOT_PORT))

except RuntimeError:
    print(
        "Can't connect to Naoqi at ip \"" + ROBOT_IP + "\" on port " + ROBOT_PORT + ".\n" + "Please check your script arguments. Run with -h option for help.")
    sys.exit(1)

current_hour = datetime.datetime.today().hour

if (current_hour < 12):
    tts.say("Good morning! Welcome to Robot Library! Please show me your code to identify yourself!")
elif (current_hour < 19):
    tts.say("Good afternoon! Welcome to Robot Library! Please show me your code to identify yourself!")
elif (current_hour <= 24):
    tts.say("Good evening! Welcome to Robot Library! Please show me your code to identify yourself!")

identity = barcode_reader(session)
tts.say("Barcode has read.")
name = str(identity[0][0]).split(',')[0]
id_number = str(identity[0][0]).split(',')[1]
numberOfBorrowedBooks = int(str(identity[0][0]).split(',')[2])
print("Username: " + name)
print("ID Number:" + id_number)
print("Borrowed Books: " + str(numberOfBorrowedBooks))
tts.say("Welcome!" + name)
tts.say("Your ID is: " + id_number)

if (checkBooks(numberOfBorrowedBooks) and numberOfBorrowedBooks == 0):
    print("You don't have any books in your account.")
    tts.say("You don't have any books in your account.")
elif (checkBooks(numberOfBorrowedBooks) and numberOfBorrowedBooks == 1):
    print("You borrowed " + str(numberOfBorrowedBooks) + " book.")
    tts.say("You borrowed " + str(numberOfBorrowedBooks) + " book.")
elif (checkBooks((numberOfBorrowedBooks) and numberOfBorrowedBooks > 1)):
    print("You borrowed " + str(numberOfBorrowedBooks) + " books.")
    tts.say("You borrowed " + str(numberOfBorrowedBooks) + " books.")

exit_flag_1 = False
exit_flag_2 = False

while True:

    print ("What can I do for you?")
    tts.say("What can I do for you?")

    recordAudioFromNao()
    TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
    first_answer = SpeechTransferToText(local_recordingFile)

    if any(s in first_answer for s in checklist_borrow):
        tts.say("Sure! I am going to take a picture of the book you would like to borrow")
        print ("Sure! I am going to take a picture of the book you would like to borrow")

        while True:
            photoCapture()
            TransferFile(ROBOT_IP, user, passwd, nao_photoPath, local_photoPath)
            print("transfer photo correctly!")
            print('##############################################')

            # Book Cover Matching Porcess
            db = {}

            for l in csv.reader(open("books.csv")):
                db[l[0]] = l[1:]

            useSIFT = args["sift"] > 0
            useHamming = args["sift"] == 0
            ratio = 0.7
            minMatches = 40

            if useSIFT:
                minMatches = 50
            cd = CoverDescriptor(useSIFT=useSIFT)
            cm = CoverMatcher(cd, glob.glob("./cover/*.png"),
                              ratio=ratio, minMatches=minMatches, useHamming=useHamming)

            queryImage = cv2.imread('./querys/query.png')
            gray = cv2.cvtColor(queryImage, cv2.COLOR_BGR2GRAY)
            (queryKps, queryDescs) = cd.describe(gray)

            results = cm.search(queryKps, queryDescs)

            if len(results) == 0:
                print("I could not find a match for that cover! Do you want me to take a picture again?")
                tts.say("I could not find a match for that cover! Do you want me to take a picture again?")
                recordAudioFromNao()
                TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                answer = SpeechTransferToText(local_recordingFile)
                print('##############################################')

                if "no" not in answer:
                    print("Sure")
                    tts.say("Sure!")
                else:
                    print("OK. Anything else I can do for you?")
                    tts.say("OK. Anything else I can do for you?")
                    recordAudioFromNao()
                    TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                    answer = SpeechTransferToText(local_recordingFile)
                    if "no" not in answer:
                        print ("OK.")
                        tts.say("OK.")
                        break
                    else:
                        tts.say("Good Bye!" + name)
                        print("Good Bye!" + name)
                        exit(1)
            else:
                for (i, (score, coverPath)) in enumerate(results):
                    print(str(len(results)) + " covers may match the result.")
                    tts.say(str(len(results)) + " covers may match the result.")
                    print("Calculating matching ratio...")
                    tts.say("Calculating matching ratio...")
                    if (score > 0.5):
                        (author, title) = db[coverPath[coverPath.rfind("/") + 1:]]
                        print("{}. {:.2f}% : {} - {}".format(i + 1, score * 100, author, title))
                        result = cv2.imread(coverPath)
                        cv2.imshow("Query", queryImage)
                        cv2.imshow("Result", result)
                        print('##############################################')
                        tts.say("Is this one the correct book you would like to borrow?")
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()
                        recordAudioFromNao()
                        TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                        answer = SpeechTransferToText(local_recordingFile)
                        if "no" not in answer:
                            print("Perfect! I will add this one to your account! ")
                            tts.say("Perfect! I will add this one to your account! ")
                            numberOfBorrowedBooks += 1
                            tts.say("Now you have " + str(numberOfBorrowedBooks) + " books in you account!")
                            print("Now you have " + str(numberOfBorrowedBooks) + " books in you account!")
                            print("Anything else I can do for you?")
                            tts.say('Anything else I can do for you?')
                            recordAudioFromNao()
                            TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                            answer = SpeechTransferToText(local_recordingFile)
                            if "no" not in answer:
                                print("OK")
                                tts.say("Ok!")
                                exit_flag_1 = True
                                break
                            else:
                                print ('Sure. Good Bye')
                                tts.say("Sure, Good bye")
                                exit(1)

                        else:
                            tts.say("Ok, Let me take photo again!")
                            break

                    else:
                        tts.say("Matching ratio is too low to identify for the most relevant match. Do you want me to take a photo again?")
                        print("Matching ratio is too low to identify for the most relevant match. Do you want me to take a photo again?")
                        print("##############################################")
                        recordAudioFromNao()
                        TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                        answer = SpeechTransferToText(local_recordingFile)
                        print('##############################################')
                        if "no" not in answer:
                            tts.say("OK! I will take a picture again")
                            print("OK! I will take a picture again")
                            break
                        else:
                            tts.say("OK. Anything else I can do for you?")
                            print("OK. Anything else I can do for you?")
                            recordAudioFromNao()
                            TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                            answer = SpeechTransferToText(local_recordingFile)
                            if "no" not in answer:
                                tts.say("OK!")
                                exit_flag_1 = True
                                break
                            else:
                                print ("OK, Good Bye")
                                exit(1)
            if exit_flag_1:
                break

    if any(s in first_answer for s in checklist_return):
        print("key word GET!")
        tts.say(
            "Sure! I am going to take a picture of the book you would like to return")
        print(
            "Sure! I am going to take a picture of the book you would like to return")

        while True:
            photoCapture()
            TransferFile(ROBOT_IP, user, passwd, nao_photoPath, local_photoPath)
            print("transfer photo correctly!")
            print('##############################################')

            # Book Cover Matching Porcess
            db = {}

            for l in csv.reader(open("books.csv")):
                db[l[0]] = l[1:]

            useSIFT = args["sift"] > 0
            useHamming = args["sift"] == 0
            ratio = 0.7
            minMatches = 40

            if useSIFT:
                minMatches = 50
            cd = CoverDescriptor(useSIFT=useSIFT)
            cm = CoverMatcher(cd, glob.glob("./cover/*.png"),
                              ratio=ratio, minMatches=minMatches, useHamming=useHamming)

            queryImage = cv2.imread('./querys/query.png')
            gray = cv2.cvtColor(queryImage, cv2.COLOR_BGR2GRAY)
            (queryKps, queryDescs) = cd.describe(gray)

            results = cm.search(queryKps, queryDescs)

            if len(results) == 0:
                print("I could not find a match for that cover! Do you want me to take a picture again?")
                tts.say("I could not find a match for that cover! Do you want me to take a picture again?")
                recordAudioFromNao()
                TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                answer = SpeechTransferToText(local_recordingFile)
                print('##############################################')

                if "no" not in answer:
                    print("OK.")
                    tts.say("OK.")
                else:
                    print("OK. Anything else I can do for you?")
                    tts.say("OK. Anything else I can do for you?")
                    recordAudioFromNao()
                    TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                    answer = SpeechTransferToText(local_recordingFile)
                    if "no" not in answer:
                        tts.say("Sure!")
                        break
                    else:
                        tts.say("Good Bye!" + name)
                        print("Good Bye!" + name)
                        exit(1)
            else:
                for (i, (score, coverPath)) in enumerate(results):
                    print(str(len(results)) + " covers may match the result.")
                    tts.say(str(len(results)) + " covers may match the result.")
                    print("Calculating matching ratio...")
                    tts.say("Calculating matching ratio...")
                    if (score > 0.5):
                        (author, title) = db[coverPath[coverPath.rfind("/") + 1:]]
                        print("{}. {:.2f}% : {} - {}".format(i + 1, score * 100, author, title))
                        result = cv2.imread(coverPath)
                        cv2.imshow("Query", queryImage)
                        cv2.imshow("Result", result)
                        print('##############################################')
                        tts.say("Is this one the correct book you would like to return?")
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()
                        recordAudioFromNao()
                        TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                        answer = SpeechTransferToText(local_recordingFile)
                        if "no" not in answer:
                            print("Perfect! I would remove this one to your account! ")
                            tts.say("Perfect! I would remove this one to your account! ")
                            numberOfBorrowedBooks -= 1
                            print("Now you have " + str(numberOfBorrowedBooks) + " books in you account!")
                            tts.say("Now you have " + str(numberOfBorrowedBooks) + " books in you account!")
                            print("Anything else I can do for you?")
                            tts.say('Anything else I can do for you?')
                            recordAudioFromNao()
                            TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                            answer = SpeechTransferToText(local_recordingFile)
                            if "no" not in answer:
                                tts.say("Ok!")
                                exit_flag_2 = True
                                break
                            else:
                                print('Sure, Good Bye')
                                tts.say("Sure, good bye")
                                exit(1)

                        else:
                            tts.say("Ok, Let me take photo again!")
                            break

                    else:
                        print(
                            "Matching ratio is too low to identify for the most relevant match. Do you want me to take a photo again?")
                        tts.say(
                            "Matching ratio is too low to identify for the most relevant match. Do you want me to take a photo again?")
                        print("##############################################")
                        recordAudioFromNao()
                        TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                        answer = SpeechTransferToText(local_recordingFile)
                        print('##############################################')
                        if "no" not in answer:
                            print("OK! I will take a picture again")
                            tts.say("OK! I will take a picture again")
                            break
                        else:
                            print("OK. Anything else I can do for you?")
                            tts.say("OK. Anything else I can do for you?")
                            recordAudioFromNao()
                            TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                            answer = SpeechTransferToText(local_recordingFile)
                            if "no" not in answer:
                                tts.say("Sure!")
                                exit_flag_2 = True
                                break
                            else:
                                print("OK, Good Bye")
                                exit(1)
            if exit_flag_2:
                break

    if 'no' in first_answer:
        tts.say("OK, Have a nice day")
        exit(1)
    #
    # if any(s not in first_answer for s in (checklist_borrow + checklist_return + checklist_end)):
    #     tts.say("I can't recognize you. Please say again")
    #     print ("I can't recognize you. Please say again")
