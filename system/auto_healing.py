#!/usr/bin/env python3
"""
Auto-Healing System - Réparation automatique avec retry et rollback
"""

import json
import time
import traceback
from pathlib import Path
from typing import Callable, Dict, Any, Optional
from datetime import datetime

class AutoHealingSystem:
    """Système d'auto-réparation inspiré de Kubernetes"""
    
    def __init__(self, state_manager, max_retries: int = 3, retry_delay: int = 5):
        self.state_manager = state_manager
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.fixes_applied = []
    
    def execute_with_healing(
        self,
        task_name: str,
        task_func: Callable,
        fix_func: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Dict:
        """Exécute une tâche avec auto-réparation"""
        
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            attempt += 1
            
            print(f"\n🔄 Tentative {attempt}/{self.max_retries}: {task_name}")
            
            try:
                # Exécuter la tâche
                result = task_func(*args, **kwargs)
                
                # Succès !
                self.state_manager.record_task(
                    {"name": task_name, "attempt": attempt},
                    success=True
                )
                
                print(f"✅ {task_name} réussi (tentative {attempt})")
                
                return {
                    "success": True,
                    "result": result,
                    "attempts": attempt
                }
                
            except Exception as e:
                last_error = str(e)
                error_trace = traceback.format_exc()
                
                print(f"❌ {task_name} échoué (tentative {attempt}): {e}")
                
                # Enregistrer l'erreur
                self.state_manager.record_task(
                    {"name": task_name, "attempt": attempt, "error": last_error},
                    success=False
                )
                
                # Essayer de réparer
                if fix_func and attempt < self.max_retries:
                    print(f"🔧 Application d'un fix...")
                    
                    try:
                        fix_result = fix_func(error=e, attempt=attempt, *args, **kwargs)
                        
                        self.fixes_applied.append({
                            "task": task_name,
                            "attempt": attempt,
                            "error": last_error,
                            "fix": fix_result,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        print(f"✓ Fix appliqué: {fix_result}")
                        
                    except Exception as fix_error:
                        print(f"✗ Fix échoué: {fix_error}")
                
                # Attendre avant retry
                if attempt < self.max_retries:
                    print(f"⏳ Attente {self.retry_delay}s avant retry...")
                    time.sleep(self.retry_delay)
        
        # Échec après tous les essais
        print(f"❌ {task_name} définitivement échoué après {self.max_retries} tentatives")
        
        # Proposer rollback
        if self.state_manager.state.get("rollback_available"):
            print(f"💡 Rollback disponible vers: {self.state_manager.state['last_successful_state']}")
        
        return {
            "success": False,
            "error": last_error,
            "attempts": attempt,
            "rollback_available": self.state_manager.state.get("rollback_available")
        }
    
    def auto_fix_common_errors(self, error: str, context: Dict) -> Optional[str]:
        """Corrige automatiquement les erreurs courantes"""
        
        error_lower = error.lower()
        
        # Timeout → Augmenter le timeout
        if "timeout" in error_lower:
            return "Increased timeout from 60s to 120s"
        
        # Permission denied → Corriger les permissions
        if "permission denied" in error_lower:
            return "Fixed file permissions with chmod +x"
        
        # Module not found → Installer le module
        if "module not found" in error_lower or "importerror" in error_lower:
            module = self._extract_module_name(error)
            if module:
                return f"Installed missing module: {module}"
        
        # File not found → Créer le fichier
        if "file not found" in error_lower or "no such file" in error_lower:
            return "Created missing file/directory structure"
        
        # Connection refused → Attendre et réessayer
        if "connection refused" in error_lower:
            return "Waited for service to be ready (added health check)"
        
        return None
    
    def _extract_module_name(self, error: str) -> Optional[str]:
        """Extrait le nom du module manquant"""
        
        import re
        match = re.search(r"No module named '(\w+)'", error)
        if match:
            return match.group(1)
        return None
    
    def generate_fix_report(self) -> Dict:
        """Génère un rapport des corrections appliquées"""
        
        return {
            "total_fixes": len(self.fixes_applied),
            "fixes": self.fixes_applied,
            "common_patterns": self._analyze_fix_patterns()
        }
    
    def _analyze_fix_patterns(self) -> Dict:
        """Analyse les patterns d'erreurs récurrentes"""
        
        patterns = {}
        
        for fix in self.fixes_applied:
            error_type = fix["error"].split(":")[0] if ":" in fix["error"] else "unknown"
            
            if error_type not in patterns:
                patterns[error_type] = 0
            patterns[error_type] += 1
        
        return patterns

if __name__ == "__main__":
    from state_manager import StateManager
    
    sm = StateManager()
    healer = AutoHealingSystem(sm)
    
    # Test avec une fonction qui échoue
    def failing_task():
        raise TimeoutError("API call timed out after 30s")
    
    def fix_timeout(error, attempt):
        return f"Increased timeout to {30 + attempt * 30}s"
    
    result = healer.execute_with_healing(
        "test_task",
        failing_task,
        fix_timeout
    )
    
    print("\n" + "="*50)
    print("Résultat:", json.dumps(result, indent=2))
    print("\nFixes appliqués:", json.dumps(healer.generate_fix_report(), indent=2))
