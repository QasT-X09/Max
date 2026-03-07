import fitz
import pytesseract
import os
from PIL import Image
import io

# путь к OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\AI\tesseract\tesseract.exe"

pdf_path = "test.pdf"

# папка для изображений
output_folder = "images"
os.makedirs(output_folder, exist_ok=True)

pdf = fitz.open(pdf_path)

image_count = 0

print("Начинаю анализ PDF...\n")

for page_index in range(len(pdf)):

    page = pdf[page_index]

    images = page.get_images(full=True)

    print(f"Страница {page_index+1}, найдено изображений:", len(images))

    for img in images:

        xref = img[0]

        base_image = pdf.extract_image(xref)

        image_bytes = base_image["image"]

        image_ext = base_image["ext"]

        image = Image.open(io.BytesIO(image_bytes))

        image_name = f"{output_folder}/image_{image_count}.{image_ext}"

        image.save(image_name)

        print(f"\nИзображение сохранено: {image_name}")

        text = pytesseract.image_to_string(image)

        print("Распознанный текст:")

        print(text)

        print("-"*40)

        image_count += 1

print("\nАнализ завершён.")