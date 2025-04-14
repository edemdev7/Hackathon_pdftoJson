import os
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://sgg.gouv.bj"
SAVE_DIR = "cm"  # Répertoire où stocker les PDFs

# Vérifie et crée le dossier de stockage si nécessaire
os.makedirs(SAVE_DIR, exist_ok=True)

def get_pdf_links_and_decrees(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    pdf_links = []
    next_page_url = None

    for a in soup.find_all('a', href=True):
        href = a['href']

        # Récupération des liens de téléchargement PDF
        if "/download" in href:
            full_url = BASE_URL + href if href.startswith('/') else href
            pdf_links.append(full_url)


        # Vérifie si le bouton "Suivant" est présent et actif
        if "Suivant" in a.text and "disable" not in a.get("class", []):
            next_page_url = a["href"] if a["href"].startswith("http") else BASE_URL + a["href"]

    return pdf_links, next_page_url

def download_pdf(url):
    filename = "Conseil des Ministres du  " + url.split("/")[-2] + ".pdf"  # Préfixe ajouté
    filepath = os.path.join(SAVE_DIR, filename)

    if os.path.exists(filepath):
        print(f"⚠️ Déjà téléchargé : {filename}")
        return

    print(f"✅ Téléchargement en cours : {filename}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"✅ Téléchargé : {filename}")
    else:
        print(f"❌ Erreur de téléchargement : {url}")

# URL de départ
search_url = "https://sgg.gouv.bj/recherche/?type=cm&begin=2024-01-01&end=2024-12-31&keywords="

while search_url:
    print(f"\n📄 Scraping de la page : {search_url}")
    pdf_links, search_url = get_pdf_links_and_decrees(search_url)

    for link in pdf_links:
        download_pdf(link)

