#!/usr/bin/env python3
"""
Multi-Provider LLM Client - Supporte plusieurs providers gratuits
"""

import os
import json
import requests
from typing import Dict, Optional, List
from pathlib import Path

class MultiProviderClient:
    """Client multi-provider pour LLM avec fallback automatique"""
    
    PROVIDERS = {
        "ollama_local": {
            "name": "Ollama Local",
            "models": ["llama3.2:1b", "llama3.2", "phi3:mini", "mistral:7b"],
            "requires_auth": False,
            "base_url": "http://localhost:11434",
            "free": True
        },
        "ollama_cloud": {
            "name": "Ollama Cloud",
            "models": ["minimax-m2.7:cloud"],
            "requires_auth": True,
            "base_url": "https://api.ollama.com",
            "free": True,
            "auth_env": "OLLAMA_API_KEY"
        },
        "openrouter": {
            "name": "OpenRouter",
            "models": [
                "meta-llama/llama-3.2-3b-instruct:free",
                "mistralai/mistral-7b-instruct:free",
                "google/gemma-7b-it:free",
                "qwen/qwen-2-7b-instruct:free"
            ],
            "requires_auth": True,
            "base_url": "https://openrouter.ai/api/v1",
            "free": True,
            "auth_env": "OPENROUTER_API_KEY"
        },
        "mistral": {
            "name": "Mistral AI",
            "models": ["mistral-tiny", "mistral-small", "mistral-medium"],
            "requires_auth": True,
            "base_url": "https://api.mistral.ai/v1",
            "free": True,
            "auth_env": "MISTRAL_API_KEY"
        },
        "groq": {
            "name": "Groq",
            "models": ["llama-3.2-1b-preview", "llama-3.2-3b-preview", "mixtral-8x7b-32768"],
            "requires_auth": True,
            "base_url": "https://api.groq.com/openai/v1",
            "free": True,
            "auth_env": "GROQ_API_KEY"
        },
        "google": {
            "name": "Google Gemini",
            "models": ["gemini-flash-latest", "gemini-pro"],
            "requires_auth": True,
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "free": True,
            "auth_env": "GOOGLE_API_KEY"
        }
    }
    
    def __init__(self, config_file: str = "llm_providers.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.current_provider = None
        self.current_model = None
    
    def load_config(self) -> Dict:
        """Charge la configuration des providers"""
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Configuration par défaut
        default_config = {
            "providers": self.PROVIDERS,
            "priority": ["ollama_local", "openrouter", "mistral", "groq", "ollama_cloud"],
            "api_keys": {
                "openrouter": os.environ.get("OPENROUTER_API_KEY", ""),
                "mistral": os.environ.get("MISTRAL_API_KEY", ""),
                "groq": os.environ.get("GROQ_API_KEY", ""),
                "ollama_cloud": os.environ.get("OLLAMA_API_KEY", "")
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def get_available_providers(self) -> List[Dict]:
        """Retourne les providers disponibles avec clés API"""
        
        available = []
        
        for provider_id, provider in self.PROVIDERS.items():
            if not provider["requires_auth"]:
                available.append({
                    "id": provider_id,
                    "name": provider["name"],
                    "models": provider["models"],
                    "free": provider["free"]
                })
            else:
                # Vérifier si la clé API est présente
                key = self.config["api_keys"].get(provider_id, "")
                if key:
                    available.append({
                        "id": provider_id,
                        "name": provider["name"],
                        "models": provider["models"],
                        "free": provider["free"]
                    })
        
        return available
    
    def call(self, prompt: str, model: str = None, provider: str = None) -> str:
        """Appelle le LLM avec fallback automatique"""
        
        # Si provider spécifié, l'utiliser
        if provider:
            return self._call_provider(provider, model, prompt)
        
        # Sinon, essayer dans l'ordre de priorité
        for provider_id in self.config["priority"]:
            try:
                result = self._call_provider(provider_id, model, prompt)
                self.current_provider = provider_id
                self.current_model = model or self.PROVIDERS[provider_id]["models"][0]
                return result
            except Exception as e:
                print(f"⚠️ {provider_id} failed: {e}")
                continue
        
        raise Exception("All providers failed")
    
    def _call_provider(self, provider_id: str, model: str, prompt: str) -> str:
        """Appelle un provider spécifique"""
        
        provider = self.PROVIDERS.get(provider_id)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_id}")
        
        # Utiliser le premier modèle si non spécifié
        if not model:
            model = provider["models"][0]
        
        # Construire la requête selon le provider
        if provider_id == "ollama_local":
            return self._call_ollama_local(model, prompt)
        elif provider_id == "ollama_cloud":
            return self._call_ollama_cloud(model, prompt)
        elif provider_id == "openrouter":
            return self._call_openrouter(model, prompt)
        elif provider_id == "mistral":
            return self._call_mistral(model, prompt)
        elif provider_id == "groq":
            return self._call_groq(model, prompt)
        elif provider_id == "google":
            return self._call_google(model, prompt)
        else:
            raise ValueError(f"Unsupported provider: {provider_id}")
    
    def _call_ollama_local(self, model: str, prompt: str) -> str:
        """Appelle Ollama local"""
        
        response = requests.post(
            f"{self.PROVIDERS['ollama_local']['base_url']}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120
        )
        
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Ollama error: {result['error']}")
        
        return result.get("response", "")
    
    def _call_ollama_cloud(self, model: str, prompt: str) -> str:
        """Appelle Ollama Cloud"""
        
        api_key = self.config["api_keys"].get("ollama_cloud")
        if not api_key:
            raise Exception("OLLAMA_API_KEY not set")
        
        response = requests.post(
            f"{self.PROVIDERS['ollama_cloud']['base_url']}/api/chat",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=120
        )
        
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Ollama Cloud error: {result['error']}")
        
        return result["message"]["content"]
    
    def _call_openrouter(self, model: str, prompt: str) -> str:
        """Appelle OpenRouter"""
        
        api_key = self.config["api_keys"].get("openrouter")
        if not api_key:
            raise Exception("OPENROUTER_API_KEY not set")
        
        response = requests.post(
            f"{self.PROVIDERS['openrouter']['base_url']}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/jeanCodeUnMax/cidi-demo",
                "X-Title": "AI Orchestrator"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=120
        )
        
        result = response.json()
        
        if "error" in result:
            raise Exception(f"OpenRouter error: {result['error']}")
        
        return result["choices"][0]["message"]["content"]
    
    def _call_mistral(self, model: str, prompt: str) -> str:
        """Appelle Mistral AI"""
        
        api_key = self.config["api_keys"].get("mistral")
        if not api_key:
            raise Exception("MISTRAL_API_KEY not set")
        
        response = requests.post(
            f"{self.PROVIDERS['mistral']['base_url']}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=120
        )
        
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Mistral error: {result['error']}")
        
        return result["choices"][0]["message"]["content"]
    
    def _call_groq(self, model: str, prompt: str) -> str:
        """Appelle Groq"""
        
        api_key = self.config["api_keys"].get("groq")
        if not api_key:
            raise Exception("GROQ_API_KEY not set")
        
        response = requests.post(
            f"{self.PROVIDERS['groq']['base_url']}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=120
        )
        
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Groq error: {result['error']}")
        
        return result["choices"][0]["message"]["content"]
    
    def _call_google(self, model: str, prompt: str) -> str:
        """Appelle Google Gemini"""
        
        api_key = self.config["api_keys"].get("google")
        if not api_key:
            raise Exception("GOOGLE_API_KEY not set")
        
        response = requests.post(
            f"{self.PROVIDERS['google']['base_url']}/models/{model}:generateContent",
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": api_key
            },
            json={
                "contents": [{"parts": [{"text": prompt}]}]
            },
            timeout=120
        )
        
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Google error: {result['error']}")
        
        return result["candidates"][0]["content"]["parts"][0]["text"]
    
    def set_api_key(self, provider: str, api_key: str):
        """Définit une clé API pour un provider"""
        
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}")
        
        self.config["api_keys"][provider] = api_key
        
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

# Instance globale
client = None

def get_client() -> MultiProviderClient:
    """Obtient le client multi-provider"""
    global client
    if client is None:
        client = MultiProviderClient()
    return client

if __name__ == "__main__":
    # Test
    client = get_client()
    
    print("Available providers:")
    for p in client.get_available_providers():
        print(f"  - {p['name']}: {p['models']}")
    
    # Test avec fallback
    print("\nTesting with fallback...")
    result = client.call("Say 'Hello World'")
    print(f"Provider: {client.current_provider}")
    print(f"Model: {client.current_model}")
    print(f"Response: {result[:100]}...")
