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

import nltk
from nltk.corpus import words 
from nltk.metrics.distance import edit_distance, jaccard_distance
from nltk.util import ngrams
nltk.download('words')


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
    
    def deskew(self,image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.bitwise_not(image)
        thresh = cv2.threshold(image, 0, 255,
            cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(image, M, (w, h),
            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        cv2.putText(image, "Angle: {:.2f} degrees".format(angle),
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return image