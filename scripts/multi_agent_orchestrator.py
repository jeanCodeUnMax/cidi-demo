#!/usr/bin/env python3
"""
Multi-Agent Orchestrator - Coordonne les agents atomiques
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import des agents
sys.path.append(str(Path(__file__).parent.parent / "agents"))
from css_agent import CSSAgent
from html_agent import HTMLAgent
from js_agent import JSAgent

class MultiAgentOrchestrator:
    """Orchestrateur multi-agents avec logging et runbook"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialiser les agents
        self.agents = {
            "html": HTMLAgent(str(self.log_dir / "html_agent.log")),
            "css": CSSAgent(str(self.log_dir / "css_agent.log")),
            "js": JSAgent(str(self.log_dir / "js_agent.log"))
        }
        
        # Runbook pour tracer les erreurs
        self.runbook = {
            "start_time": datetime.datetime.now().isoformat(),
            "agents_status": {},
            "tasks_completed": [],
            "errors": []
        }
    
    def log(self, agent_name: str, message: str, level: str = "INFO"):
        """Log global"""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "agent": agent_name,
            "level": level,
            "message": message
        }
        
        # Écrire dans le log global
        with open(self.log_dir / "orchestrator.log", 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{level}] [{agent_name}] {message}\n")
        
        print(f"[{agent_name}] {message}")
        
        # Mettre à jour le runbook
        if level == "ERROR":
            self.runbook["errors"].append(log_entry)
    
    def execute_agent(self, agent_name: str, method: str, *args, **kwargs) -> Any:
        """Exécute un agent avec gestion d'erreur"""
        
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent inconnu: {agent_name}")
        
        self.log(agent_name, f"Exécution: {method}")
        
        try:
            # Exécuter la méthode
            func = getattr(agent, method)
            result = func(*args, **kwargs)
            
            # Marquer comme succès
            self.runbook["agents_status"][agent_name] = "SUCCESS"
            self.runbook["tasks_completed"].append({
                "agent": agent_name,
                "method": method,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            self.log(agent_name, f"✓ {method} terminé", "SUCCESS")
            return result
            
        except Exception as e:
            # Marquer comme erreur
            self.runbook["agents_status"][agent_name] = "FAILED"
            self.log(agent_name, f"✗ {method} échoué: {str(e)}", "ERROR")
            raise
    
    def run(self, prd_content: str) -> Dict:
        """Exécute le workflow multi-agents"""
        
        self.log("Orchestrator", "Démarrage du workflow multi-agents")
        
        result = {
            "html": None,
            "css": None,
            "js": None,
            "combined": None
        }
        
        try:
            # Phase 1: HTML Agent
            self.log("Orchestrator", "Phase 1: Génération HTML")
            result["html"] = self.execute_agent(
                "html",
                "generate",
                prd_content,
                ["hero", "skills", "projects", "contact"]
            )
            
            # Phase 2: CSS Agent
            self.log("Orchestrator", "Phase 2: Génération CSS")
            result["css"] = self.execute_agent(
                "css",
                "generate",
                result["html"],
                {"theme": "dark", "responsive": True}
            )
            
            # Phase 3: JS Agent
            self.log("Orchestrator", "Phase 3: Génération JavaScript")
            result["js"] = self.execute_agent(
                "js",
                "generate",
                result["html"],
                ["navigation", "form_validation", "animations"]
            )
            
            # Phase 4: Assemblage
            self.log("Orchestrator", "Phase 4: Assemblage final")
            result["combined"] = self.assemble(result)
            
            self.log("Orchestrator", "✓ Workflow terminé avec succès", "SUCCESS")
            
        except Exception as e:
            self.log("Orchestrator", f"✗ Workflow échoué: {str(e)}", "ERROR")
            self.save_runbook()
            raise
        
        # Sauvegarder le runbook
        self.runbook["end_time"] = datetime.datetime.now().isoformat()
        self.runbook["status"] = "SUCCESS"
        self.save_runbook()
        
        return result
    
    def assemble(self, parts: Dict) -> str:
        """Assemble les parties en un fichier HTML complet"""
        
        html_content = parts["html"]
        css_content = parts["css"]
        js_content = parts["js"]
        
        # Extraire le HTML sans les blocs de code
        if "```html" in html_content:
            start = html_content.find("```html") + 7
            end = html_content.find("```", start)
            html_content = html_content[start:end].strip()
        
        # Extraire le CSS
        if "```css" in css_content:
            start = css_content.find("```css") + 7
            end = css_content.find("```", start)
            css_content = css_content[start:end].strip()
        
        # Extraire le JS
        if "```javascript" in js_content:
            start = js_content.find("```javascript") + 13
            end = js_content.find("```", start)
            js_content = js_content[start:end].strip()
        
        # Insérer le CSS dans le head
        if "</head>" in html_content:
            html_content = html_content.replace(
                "</head>",
                f"  <style>\n{css_content}\n  </style>\n</head>"
            )
        
        # Insérer le JS avant </body>
        if "</body>" in html_content:
            html_content = html_content.replace(
                "</body>",
                f"  <script>\n{js_content}\n  </script>\n</body>"
            )
        
        return html_content
    
    def save_runbook(self):
        """Sauvegarde le runbook pour diagnostic"""
        
        runbook_path = self.log_dir / "runbook.json"
        with open(runbook_path, 'w', encoding='utf-8') as f:
            json.dump(self.runbook, f, indent=2)
        
        print(f"📋 Runbook sauvegardé: {runbook_path}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python multi_agent_orchestrator.py <prd_file>")
        sys.exit(1)
    
    # Lire le PRD
    prd_path = Path(sys.argv[1])
    with open(prd_path, 'r', encoding='utf-8') as f:
        prd_content = f.read()
    
    # Exécuter l'orchestrateur
    orchestrator = MultiAgentOrchestrator()
    result = orchestrator.run(prd_content)
    
    # Sauvegarder le résultat
    output_path = Path("output") / f"{prd_path.stem}_multi_agent.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result["combined"])
    
    print(f"\n✓ Site généré: {output_path}")
    print(f"📋 Runbook: logs/runbook.json")
