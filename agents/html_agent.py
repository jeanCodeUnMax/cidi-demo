#!/usr/bin/env python3
"""
Agent HTML - Spécialisé dans la structure sémantique
"""

import os
import requests
from pathlib import Path

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.environ.get("MODEL_NAME", "minimax-m2.7:cloud")

class HTMLAgent:
    """Agent spécialisé HTML"""
    
    def __init__(self, log_file: str = "logs/html_agent.log"):
        self.name = "HTML Agent"
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """Log avec timestamp"""
        import datetime
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] [{self.name}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(f"[{self.name}] {message}")
    
    def generate(self, content_requirements: str, sections: list) -> str:
        """Génère la structure HTML"""
        
        self.log(f"Génération HTML pour {len(sections)} sections")
        
        system_prompt = """Tu es un expert HTML5. Génère UNIQUEMENT du HTML sémantique.

RÈGLES:
1. Utiliser les balises sémantiques (header, main, section, article, footer)
2. Attributs accessibilité (aria-label, role)
3. Classes BEM pour le styling
4. Commenter chaque section
5. Pas de CSS inline

FORMAT:
```html
<!-- Section: Nom -->
<section class="section-name" aria-label="Description">
  <h2>Titre</h2>
  <div class="section-name__content">
    ...
  </div>
</section>
```"""

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Requirements: {content_requirements}\nSections: {sections}"}
            ],
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{OLLAMA_HOST}/api/chat",
                json=payload,
                timeout=60
            )
            result = response.json()
            
            # Gérer différents formats de réponse Ollama
            if "message" in result and "content" in result["message"]:
                html = result["message"]["content"]
            elif "response" in result:
                html = result["response"]
            else:
                raise ValueError(f"Format de réponse inattendu: {result.keys()}")
            
            self.log(f"HTML généré: {len(html)} caractères", "SUCCESS")
            return html
            
        except Exception as e:
            self.log(f"Erreur: {str(e)}", "ERROR")
            raise

if __name__ == "__main__":
    agent = HTMLAgent()
    html = agent.generate("Portfolio personnel", ["hero", "skills", "projects"])
    print(html)
