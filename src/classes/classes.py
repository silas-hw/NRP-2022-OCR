# The main functionality of the project lies here. This includes:
#   - Image preprocessing
#   - OCR
#   - Text-to-speech
# Image capturing will be handled by the UI so don't worry about that
import pytesseract
import pyttsx3
import cv2
import re
import numpy as np

import autocorrect

import multiprocessing as mp

class OCR:

    def __init__(self, tts_rate=150):
        self.tts_rate = tts_rate
        self.img_kernel = np.array([[0, -1, 0],
                                    [-1, 5,-1],
                                    [0, -1, 0]])

        self.speller = autocorrect.Speller()

    def preprocess(self, image):
        
        image = self.resize(image)
        image = self.pixel_transform(image, 2.0, 0)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # convert to grayscale
        #image = cv2.filter2D(src=image, ddepth=-1, kernel=self.img_kernel) # sharpen

        image = self.deskew(image)
        return image

    def resize(self, image):
        w = image.shape[1]
        scale_factor = 700/w
        return cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)

    def pixel_transform(self, image, alpha, beta):
        '''
        Performs basic pixel transformations on an image, such as:
            - Altering contrast
            - Altering brightness

        Alpha Value -> Contrast
        Beta Value -> Brightness
        '''
        new_img = np.zeros(image.shape, image.dtype)
        for row in range(image.shape[0]):
            for col in range(image.shape[1]):
                for bgr in range(image.shape[2]):
                    new_img[row][col][bgr] = np.clip(alpha*image[row][col][bgr] + beta, 0, 255)
        
        return new_img

    def deskew(self, image):
        '''
        orientates an image so any text displayed is correctly aligned
        '''
        angle = self.__get_deskew_angle(image)
    
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        m = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(image, m, (w, h),
            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        if self.__get_deskew_angle(image) == 0:
            return image
        return self.deskew(image)
        
    def __get_deskew_angle(self, image):
        thresh = cv2.bitwise_not(image) # inverse colours
        thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        coords = np.column_stack(np.where(thresh > 0)) # image is thresheld so any black pixel should be text
        angle = cv2.minAreaRect(coords)[-1] # angle will be between 0 (exclusive) and 90 (inclusive)

        if angle > 45:
            angle = 90 - angle

        return angle

    def scan_image(self, image, preprocess:bool):
        if preprocess:
            image = self.preprocess(image)
        
        txt = pytesseract.image_to_string(image)
        txt = self.speller(txt) # autocorrect text to fix any minor ocr errors
        return image, txt

    def tts(self, txt):
        # run the TTS in a seperate process
        process = mp.Process(target=self.tts_callback, args=(txt, self.tts_rate))
        process.start()

    def tts_callback(self, txt, tts_rate):
        '''
        used as a target for multiprocessing

        Note: Python seems to kill 'zombie' processes as soon as their target function finishes running
        '''
        
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', tts_rate)
        tts_engine.say(txt)
        tts_engine.runAndWait()