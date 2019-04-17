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
        print(text)
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


def photoCapture():
    tts.say("Photo capturing")
    time.sleep(3)
    photo.setResolution(2)
    photo.setPictureFormat("png")
    photo.takePictures(1, "/home/nao/Library/queryTemp/", "query")


def checkBooks(numberOfBorrowedBooks):
    if numberOfBorrowedBooks > 0:
        return True
    else:
        return False

def checkCoverMatch(score):
    if (score >= 0.5):
        return True
    else:
        tts.say("I could not find a match for that cover!")
        print("I could not find a match for that cover!")

        print('##############################################')

        tts.say("Anything else I can do for you?")
        print("Anything else I can do for you?")
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
    tts.say("Good morning! Welcome to Vaasa Library! Show me your code to identify yourself!")
elif (current_hour < 19):
    tts.say("Good afternoon! Welcome to Vaasa Library! Show me your code to identify yourself!")
elif (current_hour <= 24):
    tts.say("Good evening! Welcome to Vaasa Library! Show me your code to identify yourself!")

identity = barcode_reader(session)
tts.say("Barcode has read.")
name = str(identity[0][0]).split(',')[0]
id_number = str(identity[0][0]).split(',')[1]
numberOfBorrowedBooks = int(str(identity[0][0]).split(',')[2])
print("Username: " + name)
print("Your ID Number is:" + id_number)
print("number of books: " + str(numberOfBorrowedBooks))
tts.say("Welcome!" + name + "! Your id is " + id_number)

if (checkBooks(numberOfBorrowedBooks) and numberOfBorrowedBooks == 0):
    tts.say("You don't have any books in your account.")
elif (checkBooks(numberOfBorrowedBooks) and numberOfBorrowedBooks == 1):
    tts.say("You borrowed " + str(numberOfBorrowedBooks) + " book.")
elif (checkBooks((numberOfBorrowedBooks) and numberOfBorrowedBooks > 1)):
    tts.say("You borrowed " + str(numberOfBorrowedBooks) + " books.")

while True:
    tts.say("What can I do for you?")

    exit_flag = False
    while True:

        recordAudioFromNao()

        # Start Recording from NAO AUDIO DEVICE
        # print('#########################################################')
        # print('start recording.')
        # tts.say('start recording')
        # nao_recordingFile = '/home/nao/Library/recordingTemp/recording.wav'
        # record.startMicrophonesRecording(nao_recordingFile, 'wav', 16000, (0, 0, 1, 0))
        # time.sleep(5)
        # record.stopMicrophonesRecording()
        # print('stop recording.')
        # tts.say("stop recording.")
        # print('#########################################################')

        TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
        answer = SpeechTransferToText(local_recordingFile)

        checklist_borrow = ("borrow", "take", "ladies")
        checklist_return = ("return")
        checklist_end = ("no")

        if any(s in answer for s in checklist_borrow):
            print("key word GET!")
            tts.say("Sure! I am going to take a picture of the book you would like to borrow, please put the book cover in front of my eyes")
            # take book cover picture
            # time.sleep(3)
            # photo.setResolution(2)
            # photo.setPictureFormat("png")
            # photo.takePictures(1, "/home/nao/Library/queryTemp/", "query")
            while True:
                photoCapture()
                tts.say("Finnished")

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
                print (results)

                if len(results) == 0:
                    tts.say("I could not find a match for that cover! Do you want me to take a photo again?")
                    print("I could not find a match for that cover! Do you want me to take a photo again?")
                    recordAudioFromNao()
                    TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                    answer = SpeechTransferToText(local_recordingFile)
                    print("User speaking: " + answer)
                    print('##############################################')

                    if "no" not in answer:
                        tts.say("Sure!")
                    else:
                        tts.say("OK. Anything else I can do for you?")
                        print("OK. Anything else I can do for you?")
                        recordAudioFromNao()
                        TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                        answer = SpeechTransferToText(local_recordingFile)
                        print("User speaking: " + answer)
                        if "no" not in answer:
                            tts.say("Sure!")
                            exit_flag = True
                            break
                    if exit_flag:
                        break

                    # recordAudioFromNao()
                    # answer = SpeechTransferToText(local_recordingFile)

                #     if "no" not in answer:
                #         tts.say("OK!")
                #         print("OK!")
                #         exit_flag = True
                #         break
                # if exit_flag:
                #     break
                else:
                    for (i, (score, coverPath)) in enumerate(results):
                        if (score > 0.5):
                            (author, title) = db[coverPath[coverPath.rfind("/") + 1:]]
                            print("{}. {:.2f}% : {} - {}".format(i + 1, score * 100, author, title))
                            result = cv2.imread(coverPath)
                            cv2.imshow("Query", queryImage)
                            cv2.imshow("Result", result)
                            print('##############################################')
                            tts.say("Is this one the correct book you would like to borrow?")
                            cv2.waitKey(0)
                            recordAudioFromNao()
                            answer = SpeechTransferToText()
                            if "yes" in answer:
                                tts.say("Prefect! I added this one to your account! Anything else I can do for you?")
                                numberOfBorrowedBooks += 1
                                recordAudioFromNao()
                                answer = SpeechTransferToText(local_recordingFile)
                                if "yes" in answer:
                                    tts.say("Ok!")
                                    break
                                else:
                                    exit_flag = True
                                    break
                                if exit_flag:
                                    break

                                break
                            else:
                                tts.say("Ok, Let me take photo again!")
                        else:
                            tts.say("Matching Ratio is too low to identify. Do you want me to take a photo again?")
                            print("Matching Ratio is too low to identify. Do you want me to take a photo again?")
                            print("##############################################")
                            recordAudioFromNao()
                            TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                            answer = SpeechTransferToText(local_recordingFile)
                            print("User speaking: " + answer)
                            print('##############################################')

                            if "no" not in answer:
                                tts.say("Sure!")
                            else:
                                tts.say("OK. Anything else I can do for you?")
                                print("OK. Anything else I can do for you?")
                                recordAudioFromNao()
                                TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
                                answer = SpeechTransferToText(local_recordingFile)
                                print("User speaking: " + answer)
                                if "no" not in answer:
                                    tts.say("Sure!")

                                    break
                                else:
                                    exit_flag = True
                                    break
                            if exit_flag:
                                break
                        if exit_flag:
                            break


        #
        #
        # if any(s in answer for s in checklist_return):
        #
        #
        # if any(s in answer for s in checklist_end):
        #     break

# Book Cover Matching Porcess
ap.add_argument("-s", "--sift", type=int, default=0, help="whether or not SIFT should be used")

args = vars(ap.parse_args())

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

# querying process
queryPaths = glob.glob("./querys/*.png")
for queryPath in queryPaths:
    queryImage = cv2.imread(queryPath)
    gray = cv2.cvtColor(queryImage, cv2.COLOR_BGR2GRAY)
    (queryKps, queryDescs) = cd.describe(gray)

    results = cm.search(queryKps, queryDescs)

    # for item in results:
    #     if item[0] > 0.3:
    #         cv2.imshow("Query", queryImage)

    if len(results) == 0:
        print("I could not find a match for that cover!")
        print('##############################################')

    else:
        for (i, (score, coverPath)) in enumerate(results):
            if (score > 0.5):
                (author, title) = db[coverPath[coverPath.rfind("/") + 1:]]
                print("{}. {:.2f}% : {} - {}".format(i + 1, score * 100, author, title))
                result = cv2.imread(coverPath)
                cv2.imshow("Query", queryImage)
                cv2.imshow("Result", result)
                cv2.waitKey(0)
                print('##############################################')
                tts.say("Is this one the correct book you would like to take?")
