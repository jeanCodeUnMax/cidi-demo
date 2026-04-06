# PRD: Super Mario Style Années 80 - Jeu HTML5 avec Son 8-bit

## 🎮 Concept

Un jeu de plateforme 2D inspiré de Super Mario Bros (1985) avec graphismes pixel art et son 8-bit authentique, jouable directement dans le navigateur.

---

## 📋 Fonctionnalités Principales

### Gameplay
- **Personnage jouable** : Mario-style avec animation de course et saut
- **Contrôles** : Flèches directionnelles + Espace pour sauter
- **Physique** : Gravité, collisions, plateformes
- **Ennemis** : Goombas-style avec IA simple
- **Collectibles** : Pièces, power-ups (champignon, étoile)
- **Niveaux** : 3 niveaux avec difficulté progressive
- **Score** : Système de points et vies

### Audio 8-bit
- **Musique** : Thème principal en style chiptune
- **Effets sonores** :
  - Saut (blip montant)
  - Collecte pièce (ding)
  - Power-up (fanfare)
  - Mort (descente)
  - Victoire (fanfare complète)
- **Génération** : Web Audio API pour synthèse 8-bit

### Visuels
- **Style** : Pixel art 16x16 pixels par sprite
- **Palette** : Couleurs NES authentiques
- **Animations** : 4 frames pour course, 2 pour saut
- **Parallax** : 3 couches de scrolling
- **Particles** : Effets de poussière et étoiles

---

## 🔧 Spécifications Techniques

### HTML5 Canvas
- **Résolution** : 256x240 pixels (résolution NES)
- **Scaling** : 3x pour affichage moderne (768x720)
- **Frame rate** : 60 FPS avec requestAnimationFrame

### Architecture Code
```
output-projet/
├── index.html          # Structure HTML
├── styles.css          # Styling et animations
├── game.js             # Moteur de jeu principal
├── audio.js            # Synthèse 8-bit
├── sprites.js          # Génération pixel art
├── levels.js           # Données des niveaux
└── dev-book.md         # Documentation
```

### Modules JavaScript
1. **GameEngine** : Boucle principale, états, timing
2. **Physics** : Collisions, gravité, mouvement
3. **Player** : Contrôles, animations, états
4. **Enemies** : IA, patterns, collisions
5. **Audio** : Synthèse 8-bit, musique, SFX
6. **Renderer** : Canvas, sprites, parallax
7. **Levels** : Chargement, progression

---

## 🎨 Assets à Générer

### Sprites (16x16 pixels)
- **Player** : Idle, run (4 frames), jump, death
- **Enemies** : Walk (2 frames), death
- **Tiles** : Ground, bricks, question blocks, pipes
- **Items** : Coin (4 frames rotation), mushroom, star
- **UI** : Numbers, HUD elements

### Audio
- **BGM** : 4 boucles musicales (thème, underground, underwater, castle)
- **SFX** : 8 effets sonores

---

## 📊 Orchestration Multi-Provider

| Composant | Provider | Modèle | Spécialité |
|-----------|----------|--------|------------|
| **HTML** | Mistral | mistral-small | Structure sémantique |
| **CSS** | Groq | llama-3.3-70b-versatile | Animations, responsive |
| **JS** | Google Gemini | gemini-flash-latest | Logique jeu, audio |

---

## ✅ Critères de Succès

1. **Jouable** : Contrôles fluides, pas de bugs
2. **Performance** : 60 FPS constant
3. **Audio** : Son 8-bit fonctionnel
4. **Visuel** : Pixel art authentique
5. **Progression** : 3 niveaux complets
6. **Dev-book** : Documentation complète

---

## 🚀 Commandes de Test

```bash
# Lancer le jeu
open output-projet/index.html

# Tester l'audio
# Cliquer sur l'écran pour activer le son

# Contrôles
# ← → : Déplacement
# Espace : Saut
# R : Restart
```

---

## 📈 Métriques de Test

| Métrique | Objectif |
|----------|----------|
| Temps de chargement | < 1 seconde |
| FPS | 60 constant |
| Taille totale | < 100 KB |
| Compatibilité | Chrome, Firefox, Safari |
| Mobile | Responsive |

---

## 🎯 Objectif du Test

Évaluer les limites de compréhension et d'exécution des modèles :
- **Cohérence** : Code fonctionnel sans bugs
- **Complétude** : Toutes les features implémentées
- **Qualité** : Code propre et documenté
- **Performance** : Optimisations présentes
- **Créativité** : Solutions originales

---

_Généré pour test multi-provider orchestration_

> 🎮 v1 - Test GitHub Actions
