#!/usr/bin/env python3
"""
Script qui lit un PRD et génère un site web HTML/CSS via Ollama
"""

import os
import sys
import json
import requests
from pathlib import Path

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.environ.get("MODEL_NAME", "phi3:mini")
PRD_DIR = Path(os.environ.get("PRD_DIR", "prd"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "output"))

def read_prd(prd_file: str) -> str:
    """Lit le contenu du fichier PRD"""
    prd_path = PRD_DIR / prd_file
    if not prd_path.exists():
        raise FileNotFoundError(f"PRD non trouvé: {prd_path}")
    
    with open(prd_path, 'r', encoding='utf-8') as f:
        return f.read()

def call_ollama(prompt: str) -> str:
    """Appelle l'API Ollama pour générer le code"""
    url = f"{OLLAMA_HOST}/api/generate"
    
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
    
    print(f"Appel à Ollama avec le modèle {MODEL_NAME}...")
    response = requests.post(url, json=payload, timeout=300)
    response.raise_for_status()
    
    result = response.json()
    return result.get("response", "")

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
    
    # Appeler Ollama
    response = call_ollama(prompt)
    
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
