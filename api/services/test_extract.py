import os
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageOps

INPUT_FOLDER = "downloads"
OUTPUT_FOLDER = "extracted_texts"
POPPLER_PATH = "/usr/bin"  # Mettre à jour si nécessaire
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Langue OCR — installer le pack fr avec `sudo apt install tesseract-ocr-fra`
OCR_LANG = "fra+eng"
OCR_CONFIG = "--psm 6"  # Bonne précision pour des blocs de texte

def extract_text_from_pdf(pdf_path):
    """ Essaie d'extraire le texte directement d'un PDF """
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text("text")

    return text.strip()

def preprocess_image(pil_image):
    """ Améliore la qualité de l'image avant OCR """
    image = pil_image.convert("L")  # Grayscale
    image = ImageOps.invert(image)  # Inverser noir/blanc si nécessaire
    image = image.filter(ImageFilter.MedianFilter())  # Supprime bruit léger
    image = ImageOps.autocontrast(image)
    return image

def extract_text_from_images(pdf_path):
    """ Convertit un PDF en images et utilise Tesseract OCR avec traitement """
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    extracted_text = ""

    for i, img in enumerate(images):
        print(f"🖼️  OCR sur la page {i+1}")
        processed_img = preprocess_image(img)
        text = pytesseract.image_to_string(processed_img, lang=OCR_LANG, config=OCR_CONFIG)

        # Nettoyage basique
        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 2]
        extracted_text += "\n".join(lines) + "\n"

    return extracted_text.strip()

def process_pdfs(input_folder, output_folder):
    """ Parcourt tous les PDFs du dossier et extrait le texte """
    for pdf_file in os.listdir(input_folder):
        if pdf_file.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, pdf_file)
            output_path = os.path.join(output_folder, pdf_file.replace(".pdf", ".txt"))

            print(f"\n📄 Traitement de {pdf_file}...")

            text = extract_text_from_pdf(pdf_path)

            if not text or len(text) < 20:  # Si le PDF est une image scannée ou peu de texte
                print("⚠️  Peu ou pas de texte détecté, passage à l'OCR...")
                text = extract_text_from_images(pdf_path)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"✅ Extraction terminée : {output_path}")

# 🔁 Lancer le traitement
process_pdfs(INPUT_FOLDER, OUTPUT_FOLDER)
