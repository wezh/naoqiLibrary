from __future__ import print_function

import argparse
import os
import io
import datetime
import time

#Import Folder looping API
import glob

#Import SFTP Process API
import paramiko

#Import Picture Procressing API
from coverdescriptor import CoverDescriptor
from covermatcher import CoverMatcher
import csv
import cv2

#Import NAOqi proxy API
from naoqi import *

#import google speech environment
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

#set Robot IP and PORT
global tts, audio, record, audioplayer, photo
ap = argparse.ArgumentParser()
user = "nao"
passwd = "nimdA"
ROBOT_IP = "192.168.1.105"
ROBOT_PORT = 9559

#List of Photo and Audio Path and File in NAO Robot
nao_recordingPath = "/home/nao/Library/recordingTemp/"
nao_photoPath = "/home/nao/Library/queryTemp/"
nao_recordingFile = "/home/nao/Library/recordingTemp/recording.wav"

#List of Photo and Audio File in local computer
local_recordingPath = "./recording/"
local_recordingFile = "./recording/greeting.wav"
local_photoPath = "./querys/"

#Speech to Text Method By Google Speech API
def SpeechTransferToText(speech_file):

    #connect to google speech service
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

#Transfer audio or query files from NAO Robot
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

#Conncted to NAO ROBOT
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
    print (str(e))
    exit(1)

current_hour = datetime.datetime.today().hour
print (current_hour)

if (current_hour < 12):
    tts.say("Good morning! Welcome to Vaasa Library! What can I do for you?")
elif(current_hour < 19):
    tts.say("Good afternoon! Welcome to Vaasa Library! What can I do for you?")
elif(current_hour <= 24):
    tts.say("Good evening! Welcome to Vaasa Library! What can I do for you?")

#Start Recording from NAO AUDIO DEVICE
print('#########################################################')
print('start recording.')
print('#########################################################')
nao_recordingFile = '/home/nao/Library/recordingTemp/recording.wav'
record.startMicrophonesRecording(nao_recordingFile, 'wav', 16000, (0, 0, 1, 0))
time.sleep(3)
record.stopMicrophonesRecording()
print('stop recording.')

TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)

speech = SpeechTransferToText(local_recordingFile)

CheckList = ("borrow")
if any(s in speech for s in CheckList):
    print ("key word: #borrow# GET!")
    tts.say("Sure! I am going to take a picture of the book you would like to take")
    # take book cover picture
    time.sleep(3)
    photo.setResolution(2)
    photo.setPictureFormat("png")
    photo.takePictures(1, "/home/nao/Library/queryTemp/", "query")
    tts.say("Finnished")

#Book Cover Matching Porcess
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

#transfer picture from NAO Robot to local
TransferFile(ROBOT_IP, user, passwd, nao_photoPath, local_photoPath)

#querying process
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
                print('##############################################')
                cv2.waitKey(0)