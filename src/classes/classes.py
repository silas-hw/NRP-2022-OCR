# The main functionality of the project lies here. This includes:
#   - Image preprocessing
#   - OCR
#   - Text-to-speech
# Image capturing will be handled by the UI so don't worry about that
from xmlrpc.client import Boolean
import pytesseract
import pyttsx3
import cv2
import numpy as np


class OCR:

    def __init__(self, tts_rate=150):
        self.tts_rate = 150
        self.img_kernel = np.array([[0, -1, 0],
                                    [-1, 5,-1],
                                    [0, -1, 0]])

    def preprocess(self, image):
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # convert to grayscale
        image = cv2.filter2D(src=image, ddepth=-1, kernel=self.img_kernel) # sharpen
        image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1] # threshold image

        return image
    
    def scan_image(self, image, preprocess:bool):
        if preprocess:
            image = self.preprocess(image)
            
        return image, pytesseract.image_to_string(image)

    def tts(self,text):
        # initialises the tts engine
        engine = pyttsx3.init()

        # the speed of the tts
        engine.setProperty("rate", self.tts_rate)

        # tells the tts engine what it needs to say
        engine.say(text)

        # runs the tts engine
        engine.runAndWait()