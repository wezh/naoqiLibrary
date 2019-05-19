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

from io import BytesIO
import random
import numpy as np

import tensorflow.gfile as gfile
import matplotlib.pyplot as plt
import PIL.Image as Image
import tensorflow as tf
from keras.models import load_model

NUMBER = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

CAPTCHA_CHARSET = NUMBER
CAPTCHA_LEN = 4
CAPTCHA_HEIGHT = 60
CAPTCHA_WIDTH = 160

MODEL_FILE = './model/train_demo/captcha_adam_binary_crossentropy_bs_125_epochs_300.h5'
CAPTCHA_DIR = './captcha/'

# List of Photo and Audio Path and File in NAO Robot
nao_recordingPath = "/home/nao/Library/recordingTemp/"
nao_recordingFile = "/home/nao/Library/recordingTemp/recording.wav"

# List of Photo and Audio File in local computer
local_recordingPath = "./recording/"
local_recordingFile = "./recording/recording.wav"
local_captchaPath = "./captcha/"

model = load_model(MODEL_FILE)
graph = tf.get_default_graph()


def vec2text(vector):
    if not isinstance(vector, np.ndarray):
        vector = np.asarray(vector)
    vector = np.reshape(vector, [CAPTCHA_LEN, -1])
    text = ''
    for item in vector:
        text += CAPTCHA_CHARSET[np.argmax(item)]
    return text


def rgb2gray(img):
    # Y' = 0.299 R + 0.587 G + 0.114 B
    return np.dot(img[..., :3], [0.299, 0.587, 0.114])


def random_captcha(dir):
    text = random.choice(os.listdir(dir))
    image = os.path.join(dir, text)
    return text, image


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
    tts.say("Good morning!")
elif (current_hour < 19):
    tts.say("Good afternoon!")
elif (current_hour <= 24):
    tts.say("Good evening!")

tts.say("Please show me your code to identify yourself!")

identity = barcode_reader(session)
tts.say("Barcode has read.")
name = str(identity[0][0]).split(',')[0]
id_number = str(identity[0][0]).split(',')[1]
numberOfBorrowedBooks = int(str(identity[0][0]).split(',')[2])
print("Username: " + name)
print("ID Number:" + id_number)
tts.say("Welcome!" + name)

tts.say('Do you want me to start captcha test?')

recordAudioFromNao()
TransferFile(ROBOT_IP, user, passwd, nao_recordingPath, local_recordingPath)
first_answer = SpeechTransferToText(local_recordingFile)

if 'yes' in first_answer:
    tts.say("Sure! Let's start! There will be 10 random captcha, If I guess more than half of them, then I would pass the test. Here we go!")
    count = 0
    for i in range(15):
        text, image = random_captcha('./captcha/')
        image = cv2.imread(image)
        cv2.imshow(text, image)
        image = rgb2gray(image).reshape(1, 60, 160, 1).astype('float32') / 255
        with graph.as_default():
            prediction = model.predict(image)
            prediction_text = vec2text(prediction)
            tts.say('Captcha number' + str(i) + 'is' + prediction_text)
            print('Prediction by Robot: ' + prediction_text)
            if text.rstrip('.png') == prediction_text:
                print ('I am correct!')
                tts.say('I am correct!')
                count += 1
            else:
                print ("Oh! I am wrong! Let's try again!")
                tts.say("Oh! I am wrong! Let's try again!")
        cv2.waitKey(0)

    if count > 5:
        tts.say("Wow! I am a human now!")
    else:
        tts.say("OK, I would do my robot work later.")

