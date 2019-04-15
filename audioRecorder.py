from naoqi import ALProxy
import time

global tts, audio, record, audioplayer

ROBOT_IP = "192.168.1.105"
ROBOT_PORT = 9559

#Connect to Robot
audio = ALProxy("ALAudioDevice", ROBOT_IP, ROBOT_PORT)
record = ALProxy("ALAudioRecorder", ROBOT_IP, ROBOT_PORT)
audioplayer = ALProxy("ALAudioPlayer", ROBOT_IP, ROBOT_PORT)

#Start Recording
print("Welcome to NAO Robot Platform!")
print('#########################################################')
print('start recording')
record_path = '/home/nao/recording.wav'
record.startMicrophonesRecording(record_path, 'wav', 16000, (0, 0, 1, 0))
time.sleep(1)
record.stopMicrophonesRecording()
print('record over')
