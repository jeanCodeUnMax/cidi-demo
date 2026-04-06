# 🤖 AI Orchestrator Status

> Last updated: 2026-04-06 16:11:13 UTC

## ❌ Global Status: **FAILED**

---

## 📊 Execution Summary

| Metric | Value |
|--------|-------|
| **Attempts** | 3 |
| **Fixes Applied** | 2 |
| **Rollback Available** | Yes |

---

## 🔄 Phases Status

| Phase | Status | Attempts | Errors |
|-------|--------|----------|--------|
| **Research** | 🔄 running | 10 | 0 |
| **Planning** | ⏳ pending | 0 | 0 |
| **Development** | ❌ failed | 0 | 5 |
| **Testing** | ⏳ pending | 0 | 0 |
| **Deployment** | ⏳ pending | 0 | 0 |

---

## 📈 Statistics

- **Total Tasks**: 15
- **Completed**: 0
- **Failed**: 15
- **Success Rate**: 0.0%

---

## 🚨 Recent Errors

- `2026-04-06T16:03:07.153310`: Format de réponse inattendu: dict_keys(['error'])
- `2026-04-06T16:09:31.350179`: Ollama error: unauthorized
- `2026-04-06T16:11:12.545329`: Ollama error: unauthorized

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
