#!/usr/bin/env python3
"""
Repair Agent - Analyse les erreurs et génère des corrections
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.environ.get("MODEL_NAME", "minimax-m2.7:cloud")

class RepairAgent:
    """Agent qui analyse les erreurs et propose/génère des corrections"""
    
    def __init__(self, log_file: str = "logs/repair_agent.log"):
        self.name = "Repair Agent"
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """Log avec timestamp"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] [{self.name}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(f"[{self.name}] {message}")
    
    def analyze_errors(self, execution_report: Dict) -> Dict:
        """Analyse le rapport d'exécution et identifie les problèmes"""
        
        errors = execution_report.get("state", {}).get("recent_errors", [])
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_errors": len(errors),
            "error_types": {},
            "root_causes": [],
            "suggested_fixes": []
        }
        
        # Classifier les erreurs
        for error in errors:
            message = error.get("message", "")
            
            # Identifier le type d'erreur
            if "unauthorized" in message.lower():
                error_type = "AUTH_ERROR"
                analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1
                analysis["root_causes"].append("Ollama cloud model requires authentication")
                analysis["suggested_fixes"].append({
                    "type": "config_change",
                    "description": "Use local model or add Ollama API key",
                    "action": "Change MODEL_NAME to llama3.2:1b or add OLLAMA_API_KEY"
                })
            
            elif "timeout" in message.lower():
                error_type = "TIMEOUT_ERROR"
                analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1
                analysis["root_causes"].append("Model response too slow")
                analysis["suggested_fixes"].append({
                    "type": "config_change",
                    "description": "Increase timeout or simplify prompt",
                    "action": "Increase timeout to 180s"
                })
            
            elif "format" in message.lower():
                error_type = "PARSING_ERROR"
                analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1
                analysis["root_causes"].append("Unexpected API response format")
                analysis["suggested_fixes"].append({
                    "type": "code_fix",
                    "description": "Update response parsing logic",
                    "action": "Add fallback parsing for error responses"
                })
            
            else:
                error_type = "UNKNOWN_ERROR"
                analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1
        
        self.log(f"Analysis complete: {len(analysis['root_causes'])} root causes identified")
        return analysis
    
    def generate_fix(self, analysis: Dict, original_code: str = None) -> str:
        """Génère un correctif basé sur l'analyse"""
        
        # Si erreur d'auth, utiliser un modèle local
        if "AUTH_ERROR" in analysis["error_types"]:
            self.log("Generating fix: Switch to local model")
            return """
# FIX: Use local model instead of cloud model
# Change in generate_website.py:
MODEL_NAME = os.environ.get("MODEL_NAME", "llama3.2:1b")  # Local model, no auth required

# Or pull the model first:
# ollama pull llama3.2:1b
"""
        
        # Si erreur de parsing, générer un fix de code
        if "PARSING_ERROR" in analysis["error_types"]:
            self.log("Generating fix: Update parsing logic")
            return """
# FIX: Add error response handling
try:
    result = response.json()
    if "error" in result:
        raise ValueError(f"API Error: {result['error']}")
    # Continue with normal parsing...
except KeyError as e:
    # Fallback parsing
    if "response" in result:
        return result["response"]
    raise
"""
        
        return "# No automatic fix available"
    
    def apply_fix(self, fix_type: str, fix_content: str) -> bool:
        """Applique le correctif"""
        
        if fix_type == "config_change":
            self.log(f"Applying config fix: {fix_content}")
            # Ici on pourrait modifier les fichiers de config
            return True
        
        elif fix_type == "code_fix":
            self.log(f"Applying code fix: {fix_content}")
            # Ici on pourrait modifier le code
            return True
        
        return False
    
    def run_repair_cycle(self, max_cycles: int = 3) -> Dict:
        """Exécute un cycle de réparation complet"""
        
        execution_report_path = Path("logs/execution_report.json")
        
        if not execution_report_path.exists():
            return {"success": False, "error": "No execution report found"}
        
        with open(execution_report_path, 'r', encoding='utf-8') as f:
            execution_report = json.load(f)
        
        # Si déjà succès, pas besoin de réparer
        if execution_report.get("result", {}).get("success"):
            return {"success": True, "message": "No repair needed"}
        
        # Analyser les erreurs
        analysis = self.analyze_errors(execution_report)
        
        # Sauvegarder l'analyse
        analysis_path = Path("logs/repair_analysis.json")
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        # Générer le fix
        fix = self.generate_fix(analysis)
        
        # Sauvegarder le fix
        fix_path = Path("logs/suggested_fix.md")
        with open(fix_path, 'w', encoding='utf-8') as f:
            f.write(f"# Suggested Fix\n\nGenerated: {datetime.now().isoformat()}\n\n{fix}")
        
        self.log(f"Repair analysis saved to {analysis_path}")
        self.log(f"Suggested fix saved to {fix_path}")
        
        return {
            "success": True,
            "analysis": analysis,
            "fix": fix,
            "files_created": [str(analysis_path), str(fix_path)]
        }

if __name__ == "__main__":
    agent = RepairAgent()
    result = agent.run_repair_cycle()
    print(json.dumps(result, indent=2))
