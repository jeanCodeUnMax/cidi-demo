# 🔧 Configuration des Secrets GitHub

## Problème

GitHub bloque le push car les clés API ont été détectées dans l'historique Git.

## Solution

Configurer les secrets GitHub pour stocker les clés API en toute sécurité.

---

## 📋 Étapes

### 1. Aller dans Settings

```
Repository → Settings → Secrets and variables → Actions
```

### 2. Ajouter les secrets

Cliquer sur **"New repository secret"** pour chaque clé :

| Secret Name | Value |
|-------------|-------|
| `MISTRAL_API_KEY` | `<your-mistral-api-key>` |
| `GROQ_API_KEY` | `<your-groq-api-key>` |
| `GOOGLE_API_KEY` | `<your-google-api-key>` |
| `OPENROUTER_API_KEY` | `<your-openrouter-api-key>` |

### 3. Débloquer le push

Après avoir ajouté les secrets, aller sur :
```
https://github.com/jeanCodeUnMax/cidi-demo/security/secret-scanning
```

Cliquer sur **"Allow"** pour débloquer le secret.

---

## 🚀 Architecture Finale

```
┌─────────────────────────────────────────────────────────┐
│           MULTI-PROVIDER ORCHESTRATOR                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. Orchestrateur (découpe les tâches)                   │
│     ↓                                                     │
│  2. Agent HTML ──→ Mistral (mistral-small)               │
│     ↓                                                     │
│  3. Agent CSS ───→ Groq (llama-3.3-70b-versatile)        │
│     ↓                                                     │
│  4. Agent JS ────→ Google Gemini (gemini-flash)          │
│     ↓                                                     │
│  5. Fusion + Déploiement GitHub Pages                    │
│     ↓                                                     │
│  6. Webbook (statut visible)                             │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Fichiers Créés

| Fichier | Description |
|---------|-------------|
| `.github/workflows/multi_provider_orchestrator.yml` | Workflow principal |
| `scripts/generate_webbook.py` | Générateur de webbook |
| `llm_providers.json` | Config des providers (sans clés) |

---

## 🔗 URLs

- **Site**: https://jeancodeunmax.github.io/cidi-demo/
- **Actions**: https://github.com/jeanCodeUnMax/cidi-demo/actions
- **Secrets**: https://github.com/jeanCodeUnMax/cidi-demo/settings/secrets/actions

---

## ⚠️ Note Importante

Les clés API doivent être configurées dans les **GitHub Secrets**, jamais dans le code.

Le workflow utilisera automatiquement les secrets via :
```yaml
${{ secrets.MISTRAL_API_KEY }}
${{ secrets.GROQ_API_KEY }}
${{ secrets.GOOGLE_API_KEY }}
```
