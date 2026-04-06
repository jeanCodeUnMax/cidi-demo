#!/usr/bin/env python3
"""
Agent JavaScript - Spécialisé dans l'interactivité
"""

import os
import requests
from pathlib import Path

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.environ.get("MODEL_NAME", "minimax-m2.7:cloud")

class JSAgent:
    """Agent spécialisé JavaScript"""
    
    def __init__(self, log_file: str = "logs/js_agent.log"):
        self.name = "JS Agent"
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
    
    def generate(self, html_structure: str, interactions: list) -> str:
        """Génère le JavaScript pour l'interactivité"""
        
        self.log(f"Génération JS pour {len(interactions)} interactions")
        
        system_prompt = """Tu es un expert JavaScript vanilla. Génère UNIQUEMENT du JS ES6+.

RÈGLES:
1. Utiliser querySelector/querySelectorAll
2. Event delegation quand possible
3. Fonctions fléchées
4. Async/await pour fetch
5. Gestion d'erreurs try/catch
6. Commenter les fonctions

FORMAT:
```javascript
// Fonction: Description
const functionName = () => {
  // Implementation
};

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
  // Init
});
```"""

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"HTML:\n{html_structure}\n\nInteractions: {interactions}"}
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
                js = result["message"]["content"]
            elif "response" in result:
                js = result["response"]
            else:
                raise ValueError(f"Format de réponse inattendu: {result.keys()}")
            
            self.log(f"JS généré: {len(js)} caractères", "SUCCESS")
            return js
            
        except Exception as e:
            self.log(f"Erreur: {str(e)}", "ERROR")
            raise

if __name__ == "__main__":
    agent = JSAgent()
    js = agent.generate("<button class='btn'>Click</button>", ["click handler", "form validation"])
    print(js)
