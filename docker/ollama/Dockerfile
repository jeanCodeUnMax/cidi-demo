# Dockerfile pour Ollama avec modèle léger pré-installé
FROM ollama/ollama:latest

# Définir le modèle léger à utiliser (phi3:mini = ~2GB, très rapide)
ENV MODEL_NAME=phi3:mini

# Créer le script de démarrage qui télécharge le modèle automatiquement
RUN mkdir -p /scripts
COPY start.sh /scripts/start.sh
RUN chmod +x /scripts/start.sh

# Exposer le port Ollama
EXPOSE 11434

# Démarrer Ollama et pré-télécharger le modèle
ENTRYPOINT ["/scripts/start.sh"]
