#!/usr/bin/env python3
"""
Status Generator - Génère un fichier STATUS.md visible après chaque exécution
"""

import json
from pathlib import Path
from datetime import datetime

def generate_status_report(execution_report_path: str = "logs/execution_report.json"):
    """Génère un rapport de statut lisible"""
    
    status_file = Path("STATUS.md")
    execution_report = Path(execution_report_path)
    
    if not execution_report.exists():
        return
    
    with open(execution_report, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # Déterminer le statut global
    if report["result"]["success"]:
        status_emoji = "✅"
        status_text = "SUCCESS"
        color = "green"
    else:
        status_emoji = "❌"
        status_text = "FAILED"
        color = "red"
    
    # Générer le rapport
    content = f"""# 🤖 AI Orchestrator Status

> Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

## {status_emoji} Global Status: **{status_text}**

---

## 📊 Execution Summary

| Metric | Value |
|--------|-------|
| **Attempts** | {report["result"]["attempts"]} |
| **Fixes Applied** | {report["fixes"]["total_fixes"]} |
| **Rollback Available** | {"Yes" if report["result"]["rollback_available"] else "No"} |

---

## 🔄 Phases Status

| Phase | Status | Attempts | Errors |
|-------|--------|----------|--------|
"""
    
    for phase_name, phase_data in report["state"]["phases"].items():
        status_icon = {
            "pending": "⏳",
            "running": "🔄",
            "success": "✅",
            "failed": "❌"
        }.get(phase_data["status"], "❓")
        
        error_count = len(phase_data.get("errors", []))
        content += f"| **{phase_name.title()}** | {status_icon} {phase_data['status']} | {phase_data['attempts']} | {error_count} |\n"
    
    content += f"""
---

## 📈 Statistics

- **Total Tasks**: {report["state"]["statistics"]["total_tasks"]}
- **Completed**: {report["state"]["statistics"]["completed"]}
- **Failed**: {report["state"]["statistics"]["failed"]}
- **Success Rate**: {report["state"]["statistics"]["success_rate"]:.1f}%

---

## 🚨 Recent Errors

"""
    
    if report["state"]["recent_errors"]:
        for error in report["state"]["recent_errors"][-3:]:
            content += f"- `{error['timestamp']}`: {error['message']}\n"
    else:
        content += "_No recent errors_\n"
    
    content += """
---

## 📁 Generated Files

Check `output/` directory for generated files.

---

## 🔧 Quick Actions

```bash
# View execution report
cat logs/execution_report.json

# View runbook
cat logs/runbook.json

# Rollback if needed
python -c "from system.state_manager import StateManager; StateManager().rollback()"
```
"""
    
    # Sauvegarder le rapport
    with open(status_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Status report generated: {status_file}")
    return status_file

if __name__ == "__main__":
    generate_status_report()
