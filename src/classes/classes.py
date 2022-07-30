# The main functionality of the project lies here. This includes:
#   - Image preprocessing
#   - OCR
#   - Text-to-speech
# Image capturing will be handled by the UI so don't worry about that
from xmlrpc.client import Boolean
import pytesseract
import pyttsx3


class OCR:

    def __init__(self):
        pass

    def preprocess(self, image):
        return image
    
    def scan_image(self, image, preprocess:bool):
        if preprocess:
            image = self.prepocess(image)
            
        return pytesseract.image_to_string(image)

    def tts(self,text):
        # initialises the tts engine
        engine = pyttsx3.init()

        # the speed of the tts
        engine.setProperty("rate", 150)

        # tells the tts engine what it needs to say
        engine.say(text)

        # runs the tts engine
        engine.runAndWait()