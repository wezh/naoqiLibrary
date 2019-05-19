import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model
import random
from PIL import Image
from io import BytesIO
import base64
import os

NUMBER = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

CAPTCHA_CHARSET = NUMBER
CAPTCHA_LEN = 4
CAPTCHA_HEIGHT = 60
CAPTCHA_WIDTH = 160

MODEL_FILE = './model/train_demo/captcha_adam_binary_crossentropy_bs_125_epochs_300.h5'
CAPTCHA_DIR = './captcha/'

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

count = 0
for i in range(10):
    text, image = random_captcha('./captcha/')
    image = cv2.imread(image)
    cv2.imshow(text, image)
    image = rgb2gray(image).reshape(1, 60, 160, 1).astype('float32') / 255
    with graph.as_default():
        prediction = model.predict(image)
        prediction_text = vec2text(prediction)
        print('Prediction by Robot: ' + prediction_text)
        if text.rstrip('.png') == prediction_text:
            print ('I am correct!')
            count += 1
        else:
            print ("Oh! I am wrong! Let's try again!")
    cv2.waitKey(0)

print ("Correct rate:" + str(float(count * 10)) + "%")
if count > 5:
    print("Wow! I am a human right now!")
else:
    print("OK, I would do my robot work later.")

