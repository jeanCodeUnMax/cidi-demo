#!/usr/bin/env python3
"""
Demo Multi-Provider - Montre les providers disponibles et teste un appel
"""

import sys
sys.path.insert(0, '.')

from system.multi_provider import get_client

print("=" * 60)
print("🤖 MULTI-PROVIDER LLM CLIENT - DÉMONSTRATION")
print("=" * 60)

client = get_client()

# Afficher les providers disponibles
print("\n📋 PROVIDERS DISPONIBLES:\n")
providers = client.get_available_providers()

for p in providers:
    print(f"✅ {p['name']}")
    print(f"   Modèles: {', '.join(p['models'][:2])}...")
    print(f"   Gratuit: {'Oui' if p['free'] else 'Non'}")
    print()

# Ordre de priorité
print("🔄 ORDRE DE FALLBACK:")
for i, provider_id in enumerate(client.config["priority"], 1):
    provider = client.PROVIDERS.get(provider_id, {})
    print(f"   {i}. {provider.get('name', provider_id)}")
print()

# Tester un appel simple
print("=" * 60)
print("🧪 TEST AVEC OPENROUTER")
print("=" * 60)

try:
    result = client.call("Dis 'Hello World' en français", provider="openrouter")
    print(f"\n✅ Provider utilisé: {client.current_provider}")
    print(f"📝 Modèle: {client.current_model}")
    print(f"\n💬 Réponse:\n{result}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("🧪 TEST AVEC MISTRAL")
print("=" * 60)

try:
    result = client.call("Dis 'Hello World' en français", provider="mistral")
    print(f"\n✅ Provider utilisé: {client.current_provider}")
    print(f"📝 Modèle: {client.current_model}")
    print(f"\n💬 Réponse:\n{result}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("🧪 TEST AVEC GOOGLE GEMINI")
print("=" * 60)

try:
    result = client.call("Dis 'Hello World' en français", provider="google")
    print(f"\n✅ Provider utilisé: {client.current_provider}")
    print(f"📝 Modèle: {client.current_model}")
    print(f"\n💬 Réponse:\n{result}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("🧪 TEST AVEC GROQ")
print("=" * 60)

try:
    result = client.call("Dis 'Hello World' en français", provider="groq")
    print(f"\n✅ Provider utilisé: {client.current_provider}")
    print(f"📝 Modèle: {client.current_model}")
    print(f"\n💬 Réponse:\n{result}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("✅ DÉMONSTRATION TERMINÉE")
print("=" * 60)
