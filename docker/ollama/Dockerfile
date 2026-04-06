# Dockerfile pour Ollama avec modèle léger pré-installé
FROM ollama/ollama:latest

# Définir le modèle ultra-léger (llama3.2:1b = ~1.3GB, plus rapide à télécharger)
ENV MODEL_NAME=llama3.2:1b

# Créer le script de démarrage qui télécharge le modèle automatiquement
RUN mkdir -p /scripts
COPY start.sh /scripts/start.sh
RUN chmod +x /scripts/start.sh

# Exposer le port Ollama
EXPOSE 11434

# Démarrer Ollama et pré-télécharger le modèle
ENTRYPOINT ["/scripts/start.sh"]
