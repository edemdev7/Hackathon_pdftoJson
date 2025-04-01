import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Fonction pour télécharger un fichier PDF
def download_pdf(url, folder_path):
    # Nom du fichier extrait de l'URL
    pdf_name = url.split('/')[-1]
    pdf_path = os.path.join(folder_path, pdf_name)
    
    # Télécharger le fichier PDF
    response = requests.get(url)
    with open(pdf_path, 'wb') as file:
        file.write(response.content)
    print(f'Téléchargé : {pdf_name}')

# Fonction pour scraper les liens des PDFs depuis une page
def scrape_pdfs(url, folder_path):
    # Créer le dossier si nécessaire
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Effectuer la requête HTTP et parser la page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Trouver tous les liens de téléchargement
    download_buttons = soup.find_all('a', href=True, text="Télécharger")
    
    # Extraire les URLs des PDFs à télécharger
    pdf_urls = [urljoin(url, button['href']) for button in download_buttons]
    
    # Télécharger chaque PDF
    for pdf_url in pdf_urls:
        download_pdf(pdf_url, folder_path)

# URLs des pages à scraper
url_cm = 'https://sgg.gouv.bj/recherche/?type=cm&begin=2024-01-01&end=2024-12-31&keywords='
url_decrets = 'https://sgg.gouv.bj/recherche/?type=decret&begin=2024-01-01&end=2024-12-31&keywords='

# Dossiers pour stocker les PDFs
folder_cm = './pdfs/cm'
folder_decrets = './pdfs/decrets'

# Scraper les PDFs depuis les pages des Conseils des Ministres et Décrets
scrape_pdfs(url_cm, folder_cm)
scrape_pdfs(url_decrets, folder_decrets)
