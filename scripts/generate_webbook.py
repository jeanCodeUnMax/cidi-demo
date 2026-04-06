#!/usr/bin/env python3
"""
Webbook Generator - Génère un statut visible du site
"""

import json
from pathlib import Path
from datetime import datetime

def generate_webbook(output_dir: str = "output"):
    """Génère le webbook de statut"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Vérifier les fichiers générés
    files_status = {
        "index.html": (output_path / "index.html").exists(),
        "styles.css": (output_path / "styles.css").exists(),
        "script.js": (output_path / "script.js").exists()
    }
    
    # Calculer le statut global
    all_complete = all(files_status.values())
    status_emoji = "✅" if all_complete else "🔄"
    status_text = "COMPLETE" if all_complete else "IN PROGRESS"
    
    # Générer le webbook
    content = f"""# 📊 Webbook - Statut du Site

> Dernière mise à jour: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

## {status_emoji} Statut Global: **{status_text}**

---

## 📁 Fichiers Générés

| Fichier | Status | Taille |
|---------|--------|--------|
"""
    
    for file, exists in files_status.items():
        file_path = output_path / file
        if exists and file_path.exists():
            size = file_path.stat().st_size
            content += f"| `{file}` | ✅ | {size:,} bytes |\n"
        else:
            content += f"| `{file}` | ⏳ | - |\n"
    
    content += f"""
---

## 🤖 Providers Utilisés

| Composant | Provider | Modèle |
|-----------|----------|--------|
| HTML | Mistral | mistral-small |
| CSS | Groq | llama-3.3-70b-versatile |
| JS | Google Gemini | gemini-flash-latest |

---

## 🔗 Liens

- **Site**: https://jeancodeunmax.github.io/cidi-demo/
- **Repository**: https://github.com/jeanCodeUnMax/cidi-demo
- **Actions**: https://github.com/jeanCodeUnMax/cidi-demo/actions

---

## 📋 Checklist

- [x] Orchestrateur configuré
- [x] 3 agents parallèles
- [x] Multi-provider fallback
- [x] GitHub Pages activé
- [x] Webbook généré

---

_Généré automatiquement par l'orchestrateur multi-provider_
"""
    
    # Sauvegarder
    webbook_path = output_path / "WEBBOOK.md"
    with open(webbook_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Webbook généré: {webbook_path}")
    return webbook_path

if __name__ == "__main__":
    generate_webbook()
