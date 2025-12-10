#!/usr/bin/env python3
"""
تشخيص مشكلة Perplexity API
"""

import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("PERPLEXITY_API_KEY")

print("=" * 70)
print("🔍 Debugging Perplexity API")
print("=" * 70)

print(f"\n✅ API Key loaded: {api_key[:20]}...")
print(f"✅ Key length: {len(api_key)}")
print(f"✅ Key starts with: pplx-{api_key[5:15]}...")

# اختبر الاتصال الأساسي
print("\n📡 Testing basic connection...")

try:
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4",  # اختبر نموذج واحد فقط
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 10
        },
        timeout=15
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response Headers:")
    for key, value in response.headers.items():
        print(f"   {key}: {value}")
    
    print(f"\n📊 Response Body:")
    print(json.dumps(response.json(), indent=2))

except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"\n⚠️  Check:")
    print("   1. Is PERPLEXITY_API_KEY correct?")
    print("   2. Does it still have credits?")
    print("   3. Is the internet connection working?")

