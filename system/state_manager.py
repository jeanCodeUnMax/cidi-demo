#!/usr/bin/env python3
"""
State Manager - Gère l'état du projet, roadmap et mémoire
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class StateManager:
    """Gestionnaire d'état avec persistance et rollback"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.state_dir = self.project_dir / ".state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers d'état
        self.state_file = self.state_dir / "current_state.json"
        self.roadmap_file = self.state_dir / "roadmap.json"
        self.memory_file = self.state_dir / "memory.json"
        self.history_dir = self.state_dir / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger ou initialiser l'état
        self.state = self.load_or_create_state()
    
    def load_or_create_state(self) -> Dict:
        """Charge l'état existant ou crée un nouvel état"""
        
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # État initial
        initial_state = {
            "project_name": self.project_dir.name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "idle",  # idle, running, success, failed
            "current_phase": None,
            "phases": {
                "research": {"status": "pending", "attempts": 0, "errors": []},
                "planning": {"status": "pending", "attempts": 0, "errors": []},
                "development": {"status": "pending", "attempts": 0, "errors": []},
                "testing": {"status": "pending", "attempts": 0, "errors": []},
                "deployment": {"status": "pending", "attempts": 0, "errors": []}
            },
            "completed_tasks": [],
            "failed_tasks": [],
            "artifacts": [],
            "rollback_available": False,
            "last_successful_state": None
        }
        
        self.save_state(initial_state)
        return initial_state
    
    def save_state(self, state: Optional[Dict] = None):
        """Sauvegarde l'état actuel"""
        
        state = state or self.state
        state["updated_at"] = datetime.now().isoformat()
        
        # Sauvegarder dans l'historique avant modification
        if self.state_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = self.history_dir / f"state_{timestamp}.json"
            shutil.copy(self.state_file, history_file)
            
            # Marquer rollback disponible
            state["rollback_available"] = True
            state["last_successful_state"] = str(history_file)
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    
    def update_phase(self, phase: str, status: str, error: Optional[str] = None):
        """Met à jour le statut d'une phase"""
        
        self.state["current_phase"] = phase
        self.state["phases"][phase]["status"] = status
        
        if status == "running":
            self.state["phases"][phase]["attempts"] += 1
        
        if error:
            self.state["phases"][phase]["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "message": error
            })
        
        self.save_state()
    
    def record_task(self, task: Dict, success: bool):
        """Enregistre une tâche complétée ou échouée"""
        
        task_record = {
            **task,
            "timestamp": datetime.now().isoformat(),
            "success": success
        }
        
        if success:
            self.state["completed_tasks"].append(task_record)
        else:
            self.state["failed_tasks"].append(task_record)
        
        self.save_state()
    
    def can_retry(self, phase: str, max_attempts: int = 3) -> bool:
        """Vérifie si on peut réessayer une phase"""
        
        attempts = self.state["phases"][phase]["attempts"]
        return attempts < max_attempts
    
    def rollback(self) -> bool:
        """Retourne à l'état précédent"""
        
        if not self.state.get("rollback_available"):
            print("❌ Pas de rollback disponible")
            return False
        
        last_state_file = self.state.get("last_successful_state")
        if not last_state_file or not Path(last_state_file).exists():
            print("❌ Fichier de rollback introuvable")
            return False
        
        # Charger l'état précédent
        with open(last_state_file, 'r', encoding='utf-8') as f:
            previous_state = json.load(f)
        
        # Restaurer
        previous_state["status"] = "rolled_back"
        previous_state["phases"][previous_state["current_phase"]]["status"] = "pending"
        
        self.save_state(previous_state)
        self.state = previous_state
        
        print(f"✅ Rollback vers {last_state_file}")
        return True
    
    def get_roadmap(self) -> Dict:
        """Charge ou crée la roadmap"""
        
        if self.roadmap_file.exists():
            with open(self.roadmap_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        roadmap = {
            "milestones": [],
            "current_sprint": None,
            "backlog": [],
            "completed": []
        }
        
        with open(self.roadmap_file, 'w', encoding='utf-8') as f:
            json.dump(roadmap, f, indent=2)
        
        return roadmap
    
    def add_memory(self, key: str, value: Any, tags: List[str] = None):
        """Ajoute une entrée dans la mémoire du projet"""
        
        memory = self.get_memory()
        
        entry = {
            "key": key,
            "value": value,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat()
        }
        
        memory["entries"].append(entry)
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=2)
    
    def get_memory(self) -> Dict:
        """Charge la mémoire du projet"""
        
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        memory = {"entries": []}
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=2)
        
        return memory
    
    def get_dev_book(self) -> Dict:
        """Génère un dev book complet"""
        
        return {
            "project": {
                "name": self.state["project_name"],
                "created": self.state["created_at"],
                "status": self.state["status"]
            },
            "phases": self.state["phases"],
            "statistics": {
                "total_tasks": len(self.state["completed_tasks"]) + len(self.state["failed_tasks"]),
                "completed": len(self.state["completed_tasks"]),
                "failed": len(self.state["failed_tasks"]),
                "success_rate": (
                    len(self.state["completed_tasks"]) / 
                    max(1, len(self.state["completed_tasks"]) + len(self.state["failed_tasks"]))
                ) * 100
            },
            "artifacts": self.state["artifacts"],
            "roadmap": self.get_roadmap(),
            "recent_errors": [
                error for phase in self.state["phases"].values()
                for error in phase.get("errors", [])[-5:]
            ]
        }

# Instance globale
state_manager = None

def get_state_manager(project_dir: str = ".") -> StateManager:
    """Obtient l'instance globale du StateManager"""
    global state_manager
    if state_manager is None:
        state_manager = StateManager(project_dir)
    return state_manager

if __name__ == "__main__":
    # Test
    sm = StateManager()
    
    # Simuler un workflow
    sm.update_phase("research", "running")
    sm.update_phase("research", "success")
    
    sm.update_phase("development", "running")
    sm.update_phase("development", "failed", error="Timeout exceeded")
    
    # Vérifier retry
    print(f"Can retry development: {sm.can_retry('development')}")
    
    # Afficher le dev book
    print(json.dumps(sm.get_dev_book(), indent=2))
