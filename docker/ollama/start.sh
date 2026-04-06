#!/bin/bash

# Démarrer Ollama en arrière-plan
ollama serve &

# Attendre que Ollama soit prêt
echo "Attente du démarrage d'Ollama..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 1
done

echo "Ollama est prêt !"

# Télécharger le modèle léger phi3:mini (~2GB)
echo "Téléchargement du modèle ${MODEL_NAME}..."
ollama pull ${MODEL_NAME}

echo "Modèle ${MODEL_NAME} prêt !"

# Garder le conteneur actif
wait
