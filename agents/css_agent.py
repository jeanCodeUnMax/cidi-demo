#!/usr/bin/env python3
"""
Agent CSS - Spécialisé dans la génération de styles CSS
"""

import os
import requests
from pathlib import Path

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.environ.get("MODEL_NAME", "minimax-m2.7:cloud")

class CSSAgent:
    """Agent spécialisé CSS"""
    
    def __init__(self, log_file: str = "logs/css_agent.log"):
        self.name = "CSS Agent"
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
    
    def generate(self, html_structure: str, design_requirements: dict) -> str:
        """Génère le CSS à partir de la structure HTML"""
        
        self.log(f"Début génération CSS pour {len(html_structure)} chars HTML")
        
        system_prompt = """Tu es un expert CSS. Génère UNIQUEMENT du CSS3 moderne.

RÈGLES:
1. Utiliser des variables CSS (:root)
2. Mobile-first responsive
3. Animations subtiles
4. Accessibilité (contraste, focus)
5. BEM naming convention

FORMAT:
```css
:root {
  --primary: #...;
  --secondary: #...;
}

/* Components */
.component { }

/* Responsive */
@media (max-width: 768px) { }
```"""

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Structure HTML:\n{html_structure}\n\nRequirements: {design_requirements}"}
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
            css = result["message"]["content"]
            
            self.log(f"CSS généré: {len(css)} caractères", "SUCCESS")
            return css
            
        except Exception as e:
            self.log(f"Erreur: {str(e)}", "ERROR")
            raise

if __name__ == "__main__":
    agent = CSSAgent()
    # Test
    css = agent.generate("<div class='hero'><h1>Title</h1></div>", {"theme": "dark"})
    print(css)
