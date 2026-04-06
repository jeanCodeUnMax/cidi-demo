#!/usr/bin/env python3
"""
Orchestrateur de Test Local - Génère un projet complet avec 3 agents
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du système
sys.path.insert(0, '.')

from system.multi_provider import get_client

class LocalOrchestrator:
    """Orchestrateur local pour tester les 3 providers"""
    
    def __init__(self, output_dir: str = "output-projet"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Utiliser le chemin absolu vers llm_providers.json
        config_path = Path(__file__).parent.parent / "llm_providers.json"
        self.client = get_client()
        self.client.config_file = config_path
        self.client.config = self.client.load_config()
        
        self.dev_state = {
            "project": "Super Mario 8-bit",
            "start_time": datetime.now().isoformat(),
            "phases": {},
            "errors": [],
            "metrics": {}
        }
    
    def log(self, message: str, phase: str = "info"):
        """Log avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{phase.upper()}] {message}")
    
    def update_dev_state(self, phase: str, status: str, details: dict = None):
        """Met à jour le dev-state"""
        self.dev_state["phases"][phase] = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.save_dev_state()
    
    def save_dev_state(self):
        """Sauvegarde le dev-state"""
        state_path = self.output_dir / "dev-state.json"
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(self.dev_state, f, indent=2, ensure_ascii=False)
    
    def generate_html(self, prd_content: str) -> str:
        """Génère le HTML avec Mistral"""
        self.log("Génération HTML avec Mistral...", "html")
        self.update_dev_state("html", "running")
        
        start_time = time.time()
        
        prompt = f"""Tu es un expert HTML5. Génère le fichier index.html complet pour un jeu Super Mario style années 80.

PRD:
{prd_content}

RÈGLES:
- HTML5 sémantique complet
- Canvas pour le rendu du jeu
- Structure modulaire avec scripts séparés
- Meta tags pour SEO
- Responsive design
- Commentaires clairs

Génère UNIQUEMENT le code HTML, pas d'explications."""
        
        try:
            result = self.client.call(prompt, provider="mistral")
            elapsed = time.time() - start_time
            
            # Sauvegarder
            html_path = self.output_dir / "index.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(result)
            
            self.log(f"✅ HTML généré: {len(result)} caractères en {elapsed:.1f}s", "html")
            self.update_dev_state("html", "completed", {
                "provider": "mistral",
                "model": self.client.current_model,
                "size": len(result),
                "time": elapsed
            })
            
            return result
            
        except Exception as e:
            self.log(f"❌ Erreur HTML: {e}", "html")
            self.update_dev_state("html", "failed", {"error": str(e)})
            self.dev_state["errors"].append({"phase": "html", "error": str(e)})
            raise
    
    def generate_css(self, prd_content: str) -> str:
        """Génère le CSS avec Groq"""
        self.log("Génération CSS avec Groq...", "css")
        self.update_dev_state("css", "running")
        
        start_time = time.time()
        
        prompt = f"""Tu es un expert CSS3. Génère le fichier styles.css complet pour un jeu Super Mario style années 80.

PRD:
{prd_content}

RÈGLES:
- CSS moderne avec variables CSS
- Animations CSS3 (keyframes)
- Pixel art styling
- Responsive design
- Dark mode support
- Performance optimisée

Génère UNIQUEMENT le code CSS, pas d'explications."""
        
        try:
            result = self.client.call(prompt, provider="groq")
            elapsed = time.time() - start_time
            
            # Sauvegarder
            css_path = self.output_dir / "styles.css"
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(result)
            
            self.log(f"✅ CSS généré: {len(result)} caractères en {elapsed:.1f}s", "css")
            self.update_dev_state("css", "completed", {
                "provider": "groq",
                "model": self.client.current_model,
                "size": len(result),
                "time": elapsed
            })
            
            return result
            
        except Exception as e:
            self.log(f"❌ Erreur CSS: {e}", "css")
            self.update_dev_state("css", "failed", {"error": str(e)})
            self.dev_state["errors"].append({"phase": "css", "error": str(e)})
            raise
    
    def generate_js(self, prd_content: str) -> str:
        """Génère le JavaScript avec Google Gemini"""
        self.log("Génération JavaScript avec Google Gemini...", "js")
        self.update_dev_state("js", "running")
        
        start_time = time.time()
        
        prompt = f"""Tu es un expert JavaScript et Game Development. Génère le fichier game.js complet pour un jeu Super Mario style années 80 avec son 8-bit.

PRD:
{prd_content}

RÈGLES:
- JavaScript vanilla ES6+ (pas de framework)
- Moteur de jeu complet avec:
  * Game loop 60 FPS
  * Physique (gravité, collisions)
  * Player controls (flèches + espace)
  * Enemies avec IA simple
  * Audio 8-bit avec Web Audio API
  * Sprite rendering sur Canvas
  * Niveaux multiples
- Commentaires JSDoc
- Gestion d'erreurs
- Optimisations performance

Génère UNIQUEMENT le code JavaScript, pas d'explications."""
        
        try:
            result = self.client.call(prompt, provider="google")
            elapsed = time.time() - start_time
            
            # Sauvegarder
            js_path = self.output_dir / "game.js"
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(result)
            
            self.log(f"✅ JavaScript généré: {len(result)} caractères en {elapsed:.1f}s", "js")
            self.update_dev_state("js", "completed", {
                "provider": "google",
                "model": self.client.current_model,
                "size": len(result),
                "time": elapsed
            })
            
            return result
            
        except Exception as e:
            self.log(f"❌ Erreur JavaScript: {e}", "js")
            self.update_dev_state("js", "failed", {"error": str(e)})
            self.dev_state["errors"].append({"phase": "js", "error": str(e)})
            raise
    
    def generate_dev_book(self):
        """Génère le dev-book complet"""
        self.log("Génération du dev-book...", "docs")
        
        dev_book = f"""# 📚 Dev-Book - Super Mario 8-bit

> Généré le: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 🎮 Projet

**Nom**: Super Mario Style Années 80
**Type**: Jeu HTML5 avec son 8-bit
**Technologies**: HTML5, CSS3, JavaScript ES6+, Web Audio API

---

## 🤖 Orchestration Multi-Provider

| Phase | Provider | Modèle | Status |
|-------|----------|--------|--------|
| HTML | {self.dev_state['phases'].get('html', {}).get('details', {}).get('provider', 'N/A')} | {self.dev_state['phases'].get('html', {}).get('details', {}).get('model', 'N/A')} | {self.dev_state['phases'].get('html', {}).get('status', 'N/A')} |
| CSS | {self.dev_state['phases'].get('css', {}).get('details', {}).get('provider', 'N/A')} | {self.dev_state['phases'].get('css', {}).get('details', {}).get('model', 'N/A')} | {self.dev_state['phases'].get('css', {}).get('status', 'N/A')} |
| JS | {self.dev_state['phases'].get('js', {}).get('details', {}).get('provider', 'N/A')} | {self.dev_state['phases'].get('js', {}).get('details', {}).get('model', 'N/A')} | {self.dev_state['phases'].get('js', {}).get('status', 'N/A')} |

---

## 📊 Métriques

| Fichier | Taille | Temps Génération |
|---------|--------|------------------|
| index.html | {self.dev_state['phases'].get('html', {}).get('details', {}).get('size', 0):,} bytes | {self.dev_state['phases'].get('html', {}).get('details', {}).get('time', 0):.1f}s |
| styles.css | {self.dev_state['phases'].get('css', {}).get('details', {}).get('size', 0):,} bytes | {self.dev_state['phases'].get('css', {}).get('details', {}).get('time', 0):.1f}s |
| game.js | {self.dev_state['phases'].get('js', {}).get('details', {}).get('size', 0):,} bytes | {self.dev_state['phases'].get('js', {}).get('details', {}).get('time', 0):.1f}s |

---

## 🎯 Architecture

```
output-projet/
├── index.html      # Structure HTML + Canvas
├── styles.css      # Styles et animations
├── game.js         # Moteur de jeu complet
├── dev-book.md     # Cette documentation
└── dev-state.json  # État du projet
```

---

## 🚀 Utilisation

1. **Ouvrir** `index.html` dans un navigateur
2. **Contrôles**:
   - ← → : Déplacement
   - Espace : Saut
   - R : Restart
3. **Objectif**: Collecter les pièces, éviter les ennemis, atteindre la fin du niveau

---

## 🔧 Modules JavaScript

1. **GameEngine** - Boucle principale, états
2. **Physics** - Gravité, collisions
3. **Player** - Contrôles, animations
4. **Enemies** - IA simple
5. **Audio** - Synthèse 8-bit
6. **Renderer** - Canvas rendering
7. **Levels** - Données des niveaux

---

## 📈 Tests de Performance

- [ ] 60 FPS constant
- [ ] Temps de chargement < 1s
- [ ] Pas de memory leaks
- [ ] Responsive sur mobile
- [ ] Audio sans latence

---

## 🐛 Erreurs Rencontrées

"""
        
        if self.dev_state["errors"]:
            for error in self.dev_state["errors"]:
                dev_book += f"- **{error['phase']}**: {error['error']}\n"
        else:
            dev_book += "_Aucune erreur_\n"
        
        dev_book += """
---

## ✅ Checklist Final

- [x] PRD créé
- [x] HTML généré
- [x] CSS généré
- [x] JavaScript généré
- [x] Dev-book créé
- [x] Dev-state sauvegardé

---

_Généré automatiquement par l'orchestrateur multi-provider_
"""
        
        # Sauvegarder
        dev_book_path = self.output_dir / "dev-book.md"
        with open(dev_book_path, 'w', encoding='utf-8') as f:
            f.write(dev_book)
        
        self.log(f"✅ Dev-book créé: {dev_book_path}", "docs")
    
    def run(self, prd_file: str = "ideas/super-mario-8bit.md"):
        """Exécute l'orchestration complète"""
        
        self.log("=" * 60, "info")
        self.log("🎮 ORCHESTRATEUR MULTI-PROVIDER - SUPER MARIO 8-BIT", "info")
        self.log("=" * 60, "info")
        
        # Lire le PRD
        prd_path = Path(prd_file)
        if not prd_path.exists():
            self.log(f"❌ PRD non trouvé: {prd_file}", "error")
            return False
        
        with open(prd_path, 'r', encoding='utf-8') as f:
            prd_content = f.read()
        
        self.log(f"📄 PRD chargé: {len(prd_content)} caractères", "info")
        
        # Exécuter les 3 phases
        try:
            # Phase 1: HTML (Mistral)
            html = self.generate_html(prd_content)
            
            # Phase 2: CSS (Groq)
            css = self.generate_css(prd_content)
            
            # Phase 3: JavaScript (Google)
            js = self.generate_js(prd_content)
            
            # Générer le dev-book
            self.generate_dev_book()
            
            # Finaliser le dev-state
            self.dev_state["end_time"] = datetime.now().isoformat()
            self.dev_state["status"] = "completed"
            self.save_dev_state()
            
            self.log("=" * 60, "info")
            self.log("✅ ORCHESTRATION TERMINÉE AVEC SUCCÈS", "info")
            self.log("=" * 60, "info")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Échec de l'orchestration: {e}", "error")
            self.dev_state["status"] = "failed"
            self.save_dev_state()
            return False

if __name__ == "__main__":
    orchestrator = LocalOrchestrator()
    success = orchestrator.run()
    sys.exit(0 if success else 1)
