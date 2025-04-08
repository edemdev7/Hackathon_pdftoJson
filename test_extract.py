import os
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

INPUT_FOLDER = "downloads"
OUTPUT_FOLDER = "extracted_texts"  
POPPLER_PATH = "/usr/bin"  
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """ Essaie d'extraire le texte directement d'un PDF """
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text("text")

    return text.strip()

def extract_text_from_images(pdf_path):
    """ Convertit un PDF en images et utilise Tesseract OCR pour extraire le texte """
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    extracted_text = ""

    for img in images:
        text = pytesseract.image_to_string(img)
        extracted_text += text + "\n"

    return extracted_text.strip()

def process_pdfs(input_folder, output_folder):
    """ Parcourt tous les PDFs du dossier et extrait le texte """
    for pdf_file in os.listdir(input_folder):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, pdf_file)
            output_path = os.path.join(output_folder, pdf_file.replace(".pdf", ".txt"))

            print(f"📄 Traitement de {pdf_file}...")

            text = extract_text_from_pdf(pdf_path)

            if not text:  # Si le PDF est une image scannée
                print("⚠️ Aucun texte trouvé, passage à l'OCR...")
                text = extract_text_from_images(pdf_path)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"✅ Extraction terminée : {output_path}")

# Exécution du script
process_pdfs(INPUT_FOLDER, OUTPUT_FOLDER)
