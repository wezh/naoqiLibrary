import time

from ftplib import FTP
from naoqi import ALProxy

global tts, audio, record, audioplayer

ROBOT_IP = "192.168.1.144"
ROBOT_PORT = 9559

#Connect to Robot
tts = ALProxy("ALTextToSpeech", ROBOT_IP, ROBOT_PORT)
audio = ALProxy("ALAudioDevice", ROBOT_IP, ROBOT_PORT)
record = ALProxy("ALAudioDevice", ROBOT_IP, ROBOT_PORT)
audioplayer = ALProxy("ALAudioPlayer", ROBOT_IP, ROBOT_PORT)

def record_audio(self):
    #Start Recording
    record_path = '/home/nao/recording.wav'
    record.startMicrophonesRecording(record_path, 'wav', 16000, (0, 0, 1, 0))
    time.sleep(i)
    record.stopMicrophonesRecording()
    print('record over')

def ftpconnect(host, username, password):
    ftp =  FTP()
    ftp.connect(host, 21)
    ftp.login(username, password)

def downloadRecordingFile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'wb')
    ftp.retribinary("RETR " + remotepath, fp.write, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

if __name__ == "__main__":
    ftp = ftpconnect("192.168.1.144", "nao", "nimdA")
    downloadRecordingFile(ftp, "record.wav", "record.wav")
    ftp.quit()

