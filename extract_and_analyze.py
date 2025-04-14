import os
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageOps
import json
from openai import AzureOpenAI

# === CONFIGURATION ===
INPUT_FOLDER = "downloads"
TEXT_FOLDER = "extracted_texts"
JSON_FOLDER = "structured_data"
POPPLER_PATH = "/usr/bin"  # Modifier si besoin

OCR_LANG = "fra+eng"
OCR_CONFIG = "--psm 6"

# === AZURE OPENAI CONFIG ===
AZURE_ENDPOINT = "https://instancehackatonpionners04.openai.azure.com"
AZURE_API_VERSION = "2024-05-01-preview"
AZURE_DEPLOYMENT = "gpt-4o-pionners21"

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
)

# === CRÉER LES DOSSIERS ===
os.makedirs(TEXT_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER, exist_ok=True)

# === OCR + Extraction ===
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
        print(f"🖼️ OCR sur la page {i+1}")
        processed_img = preprocess_image(img)
        text = pytesseract.image_to_string(processed_img, lang=OCR_LANG, config=OCR_CONFIG)
        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 2]
        extracted_text += "\n".join(lines) + "\n"
    return extracted_text.strip()

# === Analyse Azure GPT ===
def analyse_contenu_juridique(texte):
    prompt = f"""
Tu es un assistant juridique. Analyse le texte suivant (compte rendu ou décret) et retourne uniquement un objet JSON structuré avec les champs suivants :
- type_document (decret, compte_rendu, autre)
- numero_decret (si applicable)
- date
- ministere (ou entité concernée)
- objet
- articles (liste de titres d'articles ou paragraphes)
- signataires (liste de noms ou entités)
- autres informations pertinentes 

Réponds uniquement avec un JSON valide sans texte supplémentaire.

Texte à analyser :
\"\"\"
{texte}
\"\"\"
    """

    try:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "Tu es un assistant juridique expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        content = response.choices[0].message.content.strip()

        print("🧾 Réponse brute GPT :")
        print(content)  # Debug ici

        return json.loads(content)
    except Exception as e:
        print(f"❌ Erreur GPT Azure : {e}")
        return {
            "erreur": str(e),
            "reponse_brute": content if 'content' in locals() else "Aucune réponse"
        }


# === Pipeline principal ===
def process_pdfs(input_folder, text_folder, json_folder):
    for pdf_file in os.listdir(input_folder):
        if pdf_file.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, pdf_file)
            text_path = os.path.join(text_folder, pdf_file.replace(".pdf", ".txt"))
            json_path = os.path.join(json_folder, pdf_file.replace(".pdf", ".json"))

            print(f"\n📄 Traitement de {pdf_file}...")

            texte = extract_text_from_pdf(pdf_path)
            if not texte or len(texte) < 20:
                print("⚠️ Peu ou pas de texte détecté, passage à l'OCR...")
                texte = extract_text_from_images(pdf_path)

            with open(text_path, "w", encoding="utf-8") as f:
                f.write(texte)
            print(f"📝 Texte brut sauvegardé : {text_path}")

            print("🧠 Analyse intelligente via Azure GPT...")
            analyse = analyse_contenu_juridique(texte)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(analyse, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON structuré sauvegardé : {json_path}")

# === Lancer ===
if __name__ == "__main__":
    process_pdfs(INPUT_FOLDER, TEXT_FOLDER, JSON_FOLDER)
