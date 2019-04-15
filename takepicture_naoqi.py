import os
import sys
import time
from naoqi import ALProxy

IP = "192.168.1.145"
PORT = 9559

try:
    photoCaptureProxy = ALProxy("ALPhotoCapture", IP, PORT)
    tts = ALProxy("ALTextToSpeech", IP, PORT)
    asr = ALProxy("ALSpeechRecognition", IP, PORT)
    memory = ALProxy("ALMemory")


except Exception, e:
    print ("Error when creating ALPhotoCapture proxy:")
    print (str(e))
    exit(1)

asr.setLanguage("English")
vocabulary = ["ready", "wait", "hi", "hello"]
asr.pause(True)
asr.setVocabulary(vocabulary, False)
tts.say("Hi")

# Start the speech recognition engine with user Test_ASR
asr.subscribe("Test_ASR")
print 'Speech recognition engine started'
time.sleep(10)
asr.unsubscribe("Test_ASR")

photoCaptureProxy.setResolution(2)
photoCaptureProxy.setPictureFormat("png")
photoCaptureProxy.takePictures(1, "/home/nao/Library/querys/", "query")