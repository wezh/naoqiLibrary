import io
import os
import wave
import numpy as np
import struct

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

#credential_path = "/home/wenhao/Downloads/naoqi-f970404e0d83.json"
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

# Instantiates a client
client = speech.SpeechClient()

#Here is how 2 channels .wav file converted to 1 channel .wav file
# soundfile = wave.open('greeting.wav', 'rb')
# params = soundfile.getparams()
# nchannels, sampwidth, framerate, nframes = params[:4]
# strData = soundfile.readframes(nframes) #read format
# waveData = np.fromstring(strData, dtype=np.int16) #convert to int
# waveData = waveData * 1.0 / (max(abs(waveData))) #set one
# waveData = np.reshape(waveData, [nframes, nchannels])
# soundfile.close

# outData = waveData
# outData = np.reshape(outData, [nframes * nchannels, 1])
# outfile = 'greeting2.wav'
# outwave = wave.open(outfile, 'wb')
# nchannels = 1
# sampwidth = 2
# fs = 8000
# data_size = len(outData)
# framerate = int(fs)
# nframes = data_size
# comptype = 'NONE'
# compname = "not compressed"
# outwave.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
# for v in outData:
#     outwave.writeframes(struct.pack('h', int(v * 64000 / 2)))
# outwave.close()

# soundfile = wave.open('greeting2.wav', 'rb')
# params = soundfile.getparams()
# nchannels, sampwidth, framerate, nframes = params[:4]
# print(nchannels)
# sound_name = os.path.join(
#     os.path.dirname(__file__),
#     'greeting2.wav')

# The name of the audio file to transcribe
file_name = os.path.join(
    os.path.dirname(__file__),
    './recording/greeting.wav')

 
# Loads the audio into memory
with io.open(file_name, 'rb') as audio_file:
    content = audio_file.read()
    audio = types.RecognitionAudio(content=content)

config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code='en-US')

# Detects speech in the audio file
response = client.recognize(config, audio)

for result in response.results:
    print('Transcript: {}'.format(result.alternatives[0].transcript))