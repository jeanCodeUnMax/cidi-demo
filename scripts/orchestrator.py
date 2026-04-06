#!/usr/bin/env python3
"""
Orchestrateur IA - Détecte, planifie et exécute les projets
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Any

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.environ.get("MODEL_NAME", "minimax-m2.7:cloud")

class Orchestrator:
    def __init__(self):
        self.skills = self.load_skills()
        self.mcp_servers = self.load_mcp_config()
    
    def load_skills(self) -> Dict[str, str]:
        """Charge toutes les skills disponibles"""
        skills_dir = Path("skills")
        skills = {}
        
        if skills_dir.exists():
            for skill_file in skills_dir.glob("*.md"):
                skill_name = skill_file.stem
                with open(skill_file, 'r', encoding='utf-8') as f:
                    skills[skill_name] = f.read()
        
        return skills
    
    def load_mcp_config(self) -> Dict:
        """Charge la configuration MCP"""
        mcp_file = Path("mcp-servers.json")
        if mcp_file.exists():
            with open(mcp_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def detect_project_type(self, content: str) -> str:
        """Détecte le type de projet depuis le contenu"""
        content_lower = content.lower()
        
        if any(kw in content_lower for kw in ['portfolio', 'landing page', 'site web', 'website']):
            return 'website'
        elif any(kw in content_lower for kw in ['api', 'rest', 'graphql', 'endpoint']):
            return 'api'
        elif any(kw in content_lower for kw in ['cli', 'command line', 'terminal']):
            return 'cli'
        elif any(kw in content_lower for kw in ['library', 'package', 'npm', 'pip']):
            return 'library'
        else:
            return 'general'
    
    def create_task_plan(self, prd_content: str, project_type: str) -> List[Dict]:
        """Crée un plan de tâches structuré"""
        
        system_prompt = f"""Tu es un orchestrateur expert. Voici tes compétences:

{json.dumps(self.skills, indent=2)}

Tu as accès aux MCP servers suivants:
{json.dumps(self.mcp_servers, indent=2)}

TYPE DE PROJET DÉTECTÉ: {project_type}

Ta tâche est de créer un plan JSON avec des tâches atomiques.

FORMAT DE RÉPONSE (JSON uniquement):
{{
  "project_name": "nom-du-projet",
  "tasks": [
    {{
      "id": 1,
      "phase": "setup|research|development|testing|deployment",
      "description": "Description claire",
      "tools_needed": ["context7", "github", "npm"],
      "expected_output": "Fichier/Code attendu",
      "validation_criteria": "Comment valider"
    }}
  ]
}}

RÈGLES:
1. Commencer par la phase "research" pour enrichir les connaissances
2. Utiliser les MCP servers pertinents
3. Chaque tâche doit être atomique et mesurable
4. Prévoir des checkpoints de validation
"""

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyse ce PRD et crée un plan:\n\n{prd_content}"}
            ],
            "stream": False
        }
        
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=120
        )
        
        result = response.json()
        content = result["message"]["content"]
        
        # Extraire le JSON
        try:
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
            else:
                json_str = content
            
            return json.loads(json_str)
        except:
            return {"project_name": "unknown", "tasks": []}
    
    def execute_task(self, task: Dict, context: Dict) -> str:
        """Exécute une tâche spécifique"""
        
        system_prompt = f"""Tu es un expert technique. Voici tes compétences:

{json.dumps(self.skills, indent=2)}

TÂCHE ACTUELLE:
{json.dumps(task, indent=2)}

CONTEXTE DU PROJET:
{json.dumps(context, indent=2)}

Génère le code/résultat attendu pour cette tâche.
Utilise les meilleures pratiques actuelles.
"""

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task["description"]}
            ],
            "stream": False
        }
        
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=120
        )
        
        result = response.json()
        return result["message"]["content"]
    
    def run(self, input_file: str):
        """Point d'entrée principal"""
        
        # Lire le fichier d'entrée
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {input_file}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Détecter le type
        project_type = self.detect_project_type(content)
        print(f"Type de projet détecté: {project_type}")
        
        # Créer le plan
        plan = self.create_task_plan(content, project_type)
        print(f"Plan créé avec {len(plan.get('tasks', []))} tâches")
        
        # Exécuter chaque tâche
        context = {"project_type": project_type, "completed_tasks": []}
        
        for task in plan.get("tasks", []):
            print(f"\n▶ Phase {task['phase']}: {task['description']}")
            result = self.execute_task(task, context)
            context["completed_tasks"].append({
                "task": task,
                "result": result
            })
            print(f"✓ Tâche {task['id']} terminée")
        
        return context

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <input_file>")
        sys.exit(1)
    
    orchestrator = Orchestrator()
    result = orchestrator.run(sys.argv[1])
    
    print("\n" + "="*50)
    print("PROJET TERMINÉ")
    print("="*50)
    print(f"Tâches complétées: {len(result['completed_tasks'])}")
