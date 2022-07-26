# The main functionality of the project lies here. This includes:
#   - Image preprocessing
#   - OCR
#   - Text-to-speech
# Image capturing will be handled by the UI so don't worry about that
import pytesseract
from PIL import Image

class OCR:

    def __init__(self):
        pass

    def scan_image(self, image):
        return pytesseract.image_to_string(image)

        pass