# The main functionality of the project lies here. This includes:
#   - Image preprocessing
#   - OCR
#   - Text-to-speech
# Image capturing will be handled by the UI so don't worry about that
import pytesseract
import gtts
from playsound import playsound

class OCR:

    def __init__(self):
        pass

    def scan_image(self, image):
        return pytesseract.image_to_string(image)

        pass

    def tts(self,text):
        tts = gtts.gTTS(text)
        tts.save("tts.mp3")

        playsound("./tts.mp3")

        pass