import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import json

# Configuration de Gemini
GEMINI_API_KEY = "AIzaSyD8LKVDXO5zAFYbINcKHII-fiDa6rDexR4"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# Mappings des URLs
LANGUAGE_MAPPING = {
    "hindi": "https://fr.fiverr.com/categories/programming-tech/website-development?source=drop_down_filters&filter=auto&ref=seller_language%3Ahi",
    "bengali": "https://fr.fiverr.com/categories/programming-tech/website-development?source=drop_down_filters&filter=auto&ref=seller_language%3Abn",
    "inde": "https://fr.fiverr.com/categories/programming-tech/website-development?source=drop_down_filters&filter=auto&ref=seller_language%3Ahi"
}

BUDGET_MAPPING = {
    "50": "https://fr.fiverr.com/categories/programming-tech/website-development?source=drop_down_filters&filter=auto&ref=price%3A50",
    "moins cher": "https://fr.fiverr.com/categories/programming-tech/website-development?source=drop_down_filters&filter=auto&ref=price%3A50"
}

def analyze_query(query):
    prompt = f"""
    Analysez cette requête: "{query}"
    et identifiez:
    1. Le pays ou la langue du développeur (cherchez spécifiquement: Inde, Hindi, Bengali)
    2. Le budget (cherchez spécifiquement les montants en euros)
    
    Répondez EXACTEMENT dans ce format JSON:
    {{
        "pays_langue": "Inde ou Hindi ou Bengali ou None si non trouvé",
        "budget": "montant en euros ou None si non trouvé"
    }}

    Exemple de réponse si la requête mentionne l'Inde et 50 euros:
    {{
        "pays_langue": "Inde",
        "budget": "50"
    }}
    """
    
    response = model.generate_content(prompt)
    # Nettoyer la réponse de tout formatage markdown
    clean_response = response.text.replace('```json', '').replace('```', '').strip()
    try:
        # Remplacer "null" et "None" par Python None
        clean_response = clean_response.replace('null', 'None').replace('"None"', 'None')
        result = eval(clean_response)
        print(f"Réponse analysée: {result}")
        return result
    except Exception as e:
        print(f"Erreur lors du parsing de la réponse: {str(e)}")
        print(f"Réponse reçue: {clean_response}")
        return {"pays_langue": None, "budget": None}

def scrape_url(url):
    try:
        # En-têtes pour simuler un navigateur web
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire les informations pertinentes
            title = soup.title.string if soup.title else "No title"
            
            # Utiliser Gemini pour résumer le contenu
            content = soup.get_text(separator=' ', strip=True)[:1000]
            prompt = f"""
            Résumez les informations principales de cette page Fiverr:
            Titre: {title}
            Contenu: {content}
            
            Donnez un résumé concis en français des développeurs disponibles et leurs tarifs.
            """
            
            summary = model.generate_content(prompt)
            return summary.text
        else:
            return f"Erreur lors de l'accès à {url}: {response.status_code} - {response.text[:200]}"
    except Exception as e:
        return f"Erreur lors du scraping de {url}: {str(e)}"

# Votre requête ici
query = "Je cherche un développeur en Inde à moins de 50 euros"

# Traitement de la requête
print("Analyse de votre requête...")
analysis = analyze_query(query)
print(f"Analyse: {json.dumps(analysis, indent=2, ensure_ascii=False)}\n")

# Collecter les URLs pertinentes
urls = set()

# Ajouter l'URL pour la langue/pays
if analysis["pays_langue"]:
    pays_langue = analysis["pays_langue"].lower()
    if pays_langue in LANGUAGE_MAPPING:
        urls.add(LANGUAGE_MAPPING[pays_langue])
        print(f"URL ajoutée pour le pays/langue: {pays_langue}")

# Ajouter l'URL pour le budget
if analysis["budget"]:
    budget = analysis["budget"]
    if budget in BUDGET_MAPPING:
        urls.add(BUDGET_MAPPING[budget])
        print(f"URL ajoutée pour le budget: {budget}")

if not urls:
    print("Aucune URL correspondante trouvée pour vos critères.")
else:
    # Scraper chaque URL
    print("\nRecherche des développeurs...")
    for url in urls:
        print("\nConsultation de:", url)
        results = scrape_url(url)
        print("\nRésultats trouvés:")
        print(results)
        print("-" * 50)
