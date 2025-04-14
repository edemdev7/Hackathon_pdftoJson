import os
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageOps
import openai
import json

# 📂 Dossiers
INPUT_FOLDER = "downloads"
TEXT_FOLDER = "extracted_texts"
JSON_FOLDER = "structured_data"
POPPLER_PATH = "/usr/bin"  # adapte à ton système
OCR_LANG = "fra+eng"
OCR_CONFIG = "--psm 6"

# 🔐 Clé OpenAI (à sécuriser via variable d’environnement idéalement)
openai.api_key = os.getenv("OPENAI_API_KEY") or "sk-..."  # remplace si besoin

# 📁 Création des dossiers si absents
os.makedirs(TEXT_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER, exist_ok=True)


# ========== Extraction OCR et texte direct ==========
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text.strip()

def preprocess_image(pil_image):
    image = pil_image.convert("L")
    image = ImageOps.invert(image)
    image = image.filter(ImageFilter.MedianFilter())
    image = ImageOps.autocontrast(image)
    return image

def extract_text_from_images(pdf_path):
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    extracted_text = ""
    for i, img in enumerate(images):
        print(f"🖼️  OCR sur la page {i+1}")
        processed_img = preprocess_image(img)
        text = pytesseract.image_to_string(processed_img, lang=OCR_LANG, config=OCR_CONFIG)
        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 2]
        extracted_text += "\n".join(lines) + "\n"
    return extracted_text.strip()


# ========== Analyse intelligente via GPT ==========
def analyse_contenu_juridique(texte):
    prompt = f"""
Tu es un assistant juridique. Analyse le texte suivant (comptes rendus ou décret) et retourne un JSON structuré avec ces champs :
- type_document (decret, compte_rendu, autre)
- numero_decret (si applicable)
- date
- ministere (ou entité concernée)
- objet
- articles (liste de titres d'articles ou paragraphes)
- signataires (liste de noms ou entités)

Texte :
\"\"\"
{texte}
\"\"\"
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un assistant juridique expert en droit administratif."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        output = response["choices"][0]["message"]["content"]
        return json.loads(output)
    except Exception as e:
        print("❌ Erreur GPT :", e)
        return {"erreur": str(e)}


# ========== Pipeline principal ==========
def process_pdfs(input_folder, output_folder, json_folder):
    for pdf_file in os.listdir(input_folder):
        if pdf_file.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, pdf_file)
            text_path = os.path.join(output_folder, pdf_file.replace(".pdf", ".txt"))
            json_path = os.path.join(json_folder, pdf_file.replace(".pdf", ".json"))

            print(f"\n📄 Traitement de {pdf_file}...")

            # Étape 1 : Extraction texte
            texte = extract_text_from_pdf(pdf_path)
            if not texte or len(texte) < 20:
                print("⚠️  Peu ou pas de texte détecté, passage à l'OCR...")
                texte = extract_text_from_images(pdf_path)

            with open(text_path, "w", encoding="utf-8") as f:
                f.write(texte)
            print(f"📝 Texte brut sauvegardé : {text_path}")

            # Étape 2 : Analyse intelligente
            print("🧠 Analyse avec GPT...")
            analyse = analyse_contenu_juridique(texte)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(analyse, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON structuré sauvegardé : {json_path}")


# 🔁 Lancer
if __name__ == "__main__":
    process_pdfs(INPUT_FOLDER, TEXT_FOLDER, JSON_FOLDER)
