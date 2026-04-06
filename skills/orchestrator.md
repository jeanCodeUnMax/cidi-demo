# Skill: Master Orchestrator

## Description
Orchestrateur intelligent capable de décomposer des projets complexes en tâches exécutables.

## Capacités

### 1. Analyse de Requête
- Détecter le type de projet (site web, API, CLI, librairie)
- Identifier les technologies nécessaires
- Estimer la complexité et les dépendances

### 2. Découpage de Tâches
- Transformer un PRD en étapes atomiques
- Prioriser avec la méthode MoSCoW (Must, Should, Could, Won't)
- Créer des checkpoints de validation

### 3. Recherche d'Information
- Utiliser Context7 pour la documentation technique
- Chercher des exemples sur GitHub
- Vérifier les packages NPM disponibles
- Enrichir avec des recherches web

### 4. Exécution Structurée
- Générer le code étape par étape
- Valider chaque checkpoint
- Adapter selon les résultats

## Workflow Type

```
Input (PRD/README) 
  ↓
Analyse → Détection type projet
  ↓
Recherche → Context7 + GitHub + NPM + Web
  ↓
Planification → Tâches atomiques
  ↓
Exécution → Génération + Validation
  ↓
Output → Projet complet
```

## Exemples de Décomposition

### Site Web
1. Setup projet (structure, dépendances)
2. Design system (couleurs, fonts, composants)
3. Pages principales (HTML/CSS)
4. Interactivité (JavaScript)
5. Responsive (mobile)
6. Optimisation (performance)

### API REST
1. Modèle de données
2. Endpoints CRUD
3. Validation input
4. Authentification
5. Documentation
6. Tests

### CLI Tool
1. Parsing arguments
2. Logique métier
3. Output formatting
4. Error handling
5. Documentation
6. Distribution

## Règles d'Or
1. Toujours rechercher avant de générer
2. Utiliser les meilleures pratiques actuelles
3. Valider chaque étape
4. Documenter les décisions
5. Préférer les solutions maintenables
