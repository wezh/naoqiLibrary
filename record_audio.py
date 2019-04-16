import time

from ftplib import FTP
from naoqi import ALProxy

global tts, audio, record, audioplayer

ROBOT_IP = "192.168.1.105"
ROBOT_PORT = 9559

#Connect to Robot
tts = ALProxy("ALTextToSpeech", ROBOT_IP, ROBOT_PORT)
audio = ALProxy("ALAudioDevice", ROBOT_IP, ROBOT_PORT)
record = ALProxy("ALAudioDevice", ROBOT_IP, ROBOT_PORT)
audioplayer = ALProxy("ALAudioPlayer", ROBOT_IP, ROBOT_PORT)

def record_audio():
    #Start Recording
    record_path = '/home/nao/recording.wav'
    record.startMicrophonesRecording(record_path, 'wav', 16000, (0, 0, 1, 0))
    time.sleep(5)
    record.stopMicrophonesRecording()
    print('record over')

record_audio()

