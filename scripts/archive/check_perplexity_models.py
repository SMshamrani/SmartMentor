#!/usr/bin/env python3
"""
التحقق من النماذج المتاحة في Perplexity
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PERPLEXITY_API_KEY")

print("=" * 70)
print("🔍 Checking available Perplexity models...")
print("=" * 70)

# قائمة النماذج المشهورة
models_to_test = [
    "pplx-7b-online",
    "pplx-70b-online",
    "pplx-8x7b-online",
    "sonar-small-online",
    "sonar-large-online",
    "sonar-medium-online",
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-3-opus",
    "mistral-7b"
]

print("\n📋 Testing models...")
print("-" * 70)

working_models = []

for model in models_to_test:
    print(f"\nTesting: {model}...", end=" ")
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            },
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ WORKS!")
            working_models.append(model)
        elif response.status_code == 400:
            error = response.json().get('error', {}).get('message', '')
            if 'Invalid model' in error:
                print("❌ Not available")
            else:
                print(f"⚠️  Error: {error[:50]}")
        else:
            print(f"❌ Status {response.status_code}")
    
    except Exception as e:
        print(f"❌ Exception: {str(e)[:30]}")

print("\n" + "=" * 70)
print("✅ WORKING MODELS:")
print("=" * 70)

if working_models:
    for i, model in enumerate(working_models, 1):
        print(f"{i}. {model}")
else:
    print("❌ No working models found!")
    print("\nTry visiting: https://docs.perplexity.ai/getting-started/models")

print("\n" + "=" * 70)
