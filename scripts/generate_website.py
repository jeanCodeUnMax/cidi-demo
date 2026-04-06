#!/usr/bin/env python3
"""
Script qui lit un PRD et génère un site web HTML/CSS via Ollama Cloud API
"""

import os
import sys
import json
import requests
from pathlib import Path

# Configuration - Utilise l'API Ollama Cloud
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "https://api.ollama.ai/api/generate")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama3.2:1b")
PRD_DIR = Path(os.environ.get("PRD_DIR", "prd"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "output"))

def read_prd(prd_file: str) -> str:
    """Lit le contenu du fichier PRD"""
    prd_path = PRD_DIR / prd_file
    if not prd_path.exists():
        raise FileNotFoundError(f"PRD non trouvé: {prd_path}")
    
    with open(prd_path, 'r', encoding='utf-8') as f:
        return f.read()

def call_ollama_cloud(prompt: str) -> str:
    """Appelle l'API Ollama Cloud pour générer le code"""
    
    system_prompt = """Tu es un expert en développement web. Ta tâche est de générer du code HTML et CSS complet et fonctionnel basé sur les spécifications fournies.

RÈGLES:
1. Génère UNIQUEMENT le code HTML complet avec le CSS intégré dans une balise <style>
2. Le code doit être prêt à l'emploi, sans placeholder
3. Utilise des designs modernes et responsive
4. Inclus toutes les fonctionnalités demandées
5. Commente le code si nécessaire

Format de réponse attendu:
```html
<!DOCTYPE html>
<html>
...code complet...
</html>
```"""

    headers = {
        "Content-Type": "application/json"
    }
    
    # Ajouter l'API key si disponible
    if OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 4096
        }
    }
    
    print(f"Appel à Ollama Cloud avec le modèle {MODEL_NAME}...")
    print(f"URL: {OLLAMA_API_URL}")
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Erreur API Ollama Cloud: {e}")
        # Fallback: générer un template de base
        return generate_fallback_html(prompt)

def generate_fallback_html(prompt: str) -> str:
    """Génère un HTML de base si l'API échoue"""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Site généré (mode fallback)</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; margin-bottom: 20px; }}
        p {{ color: #666; margin-bottom: 15px; }}
        .notice {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="notice">
            ⚠️ Mode fallback activé - L'API Ollama n'était pas disponible
        </div>
        <h1>Site web généré automatiquement</h1>
        <p>Ce site a été créé à partir des spécifications suivantes:</p>
        <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto;">{prompt[:500]}...</pre>
    </div>
</body>
</html>"""

def extract_html(response: str) -> str:
    """Extrait le code HTML de la réponse"""
    # Chercher le bloc de code HTML
    if "```html" in response:
        start = response.find("```html") + 7
        end = response.find("```", start)
        if end > start:
            return response[start:end].strip()
    
    # Si pas de bloc markdown, chercher <!DOCTYPE html>
    if "<!DOCTYPE html>" in response:
        start = response.find("<!DOCTYPE html>")
        end = response.rfind("</html>") + 7
        if end > start:
            return response[start:end].strip()
    
    # Retourner tel quel si rien trouvé
    return response

def save_output(html_content: str, prd_file: str) -> str:
    """Sauvegarde le HTML généré"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Créer le nom de fichier de sortie
    base_name = Path(prd_file).stem
    output_file = OUTPUT_DIR / f"{base_name}_generated.html"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(output_file)

def main():
    # Trouver le fichier PRD le plus récent
    if not PRD_DIR.exists():
        print(f"Erreur: Dossier PRD non trouvé: {PRD_DIR}")
        sys.exit(1)
    
    prd_files = list(PRD_DIR.glob("*.md"))
    if not prd_files:
        print(f"Erreur: Aucun fichier PRD trouvé dans {PRD_DIR}")
        sys.exit(1)
    
    # Prendre le fichier le plus récent
    prd_file = max(prd_files, key=lambda p: p.stat().st_mtime)
    print(f"Utilisation du PRD: {prd_file.name}")
    
    # Lire le PRD
    prd_content = read_prd(prd_file.name)
    
    # Construire le prompt
    prompt = f"""Voici les spécifications d'un site web à créer:

{prd_content}

Génère le code HTML complet avec CSS intégré qui correspond à ces spécifications."""
    
    # Appeler Ollama Cloud
    response = call_ollama_cloud(prompt)
    
    # Extraire le HTML
    html_content = extract_html(response)
    
    # Sauvegarder
    output_path = save_output(html_content, prd_file.name)
    print(f"Site web généré: {output_path}")
    
    # Afficher un aperçu
    print("\n" + "="*50)
    print("APERÇU DU CODE GÉNÉRÉ:")
    print("="*50)
    print(html_content[:500] + "..." if len(html_content) > 500 else html_content)

if __name__ == "__main__":
    main()
