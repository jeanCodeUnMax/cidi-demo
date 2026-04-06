#!/usr/bin/env python3
"""
Script qui lit un PRD et génère un site web HTML/CSS via Ollama Cloud (model:cloud)
"""

import os
import sys
import json
import requests
from pathlib import Path

# Configuration - Utilise Ollama local
# Modèles valides: llama3.2:1b, phi3:mini, mistral:7b, etc.
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
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
    """Appelle Ollama avec un modèle cloud (model:cloud = pas de clé API)"""
    
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

    url = f"{OLLAMA_HOST}/api/chat"
    
    # Format Ollama /api/chat
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    print(f"Appel à Ollama avec le modèle cloud {MODEL_NAME}...")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        response.raise_for_status()
        
        result = response.json()
        return result["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Erreur Ollama: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response text: {e.response.text}")
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
