import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\AI\tesseract\tesseract.exe"

img = Image.open("test.png")

text = pytesseract.image_to_string(img)

print(text)