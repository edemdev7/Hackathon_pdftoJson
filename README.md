### 🚀 **Plan d’attaque**
1. **Scraping des documents**
   - Utilisation de **BeautifulSoup + Requests** ou **Scrapy** pour récupérer les PDF sur le site du gouvernement.
   - Stockage des documents en local ou sur un serveur.

2. **Extraction du texte (OCR)**
   - Utilisation de **Tesseract OCR** ou **EasyOCR** pour extraire du texte des PDFs scannés.
   - Pré-traitement des images (binarisation, redimensionnement) pour améliorer la reconnaissance.

3. **Analyse et structuration des données (NLP)**
   - Utilisation de **spaCy** ou des modèles **Hugging Face** pour identifier et structurer les entités clés :
     - Numéro du décret
     - Date
     - Ministère concerné
     - Objet du décret
     - Articles et signataires

4. **Extraction de tableaux**
   - **Tabula** pour extraire des tableaux structurés directement depuis les PDFs.

5. **Génération du fichier JSON/CSV**
   - Organisation des données extraites sous forme de JSON/CSV bien structuré.

6. **Déploiement d'une API**
   - **FastAPI** pour exposer un endpoint permettant d’envoyer un PDF et de récupérer les informations extraites.
   - Stockage en **PostgreSQL** ou JSON pour centraliser les données.

7. **Optimisation et amélioration**
   - Utilisation de **GPT-4o (via OpenAI Azure)** pour améliorer l'extraction des entités en cas d'ambiguïtés.
