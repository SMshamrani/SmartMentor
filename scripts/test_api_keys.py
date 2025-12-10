#!/usr/bin/env python3
"""
اختبار Perplexity API فقط
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def print_header(text):
    print("\n" + "=" * 70)
    print(f"🔑 {text}")
    print("=" * 70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def test_perplexity_api():
    """اختبار Perplexity API"""
    print_header("Testing Perplexity API")
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        print_error("PERPLEXITY_API_KEY not found in .env")
        return False
    
    if not api_key.startswith("pplx-"):
        print_error("Invalid Perplexity API key format")
        return False
    
    print_success(f"API Key found: {api_key[:20]}...")
    
    print("\n📡 Testing API connection...")
    
    try:
        import requests
        
        # جرب النموذج pplx-7b-online (الأكثر استقراراً)
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "pplx-7b-online",
                "messages": [
                    {
                        "role": "user",
                        "content": "What is Arduino UNO? Answer in one sentence."
                    }
                ],
                "max_tokens": 100
            },
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content']
            print_success("Perplexity API is working!")
            print(f"\n   Response: {answer[:100]}...")
            return True
        
        elif response.status_code == 401:
            print_error("Unauthorized - Invalid API Key")
            return False
        
        elif response.status_code == 400:
            error_msg = response.json().get('error', {}).get('message', 'Unknown error')
            print_error(f"Bad Request: {error_msg[:100]}")
            return False
        
        else:
            print_error(f"API Error: {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def check_dotenv():
    """التحقق من ملف .env"""
    print_header("Checking .env File")
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print_error(".env file not found")
        return False
    
    print_success(f".env file found: {env_file.absolute()}")
    
    with open(env_file, 'r') as f:
        content = f.read()
        if "PERPLEXITY_API_KEY" in content:
            print_success("PERPLEXITY_API_KEY is set")
        else:
            print_warning("PERPLEXITY_API_KEY not found in .env")
    
    return True

def check_gitignore():
    """التحقق من .gitignore"""
    print_header("Checking .gitignore")
    
    gitignore_file = Path(".gitignore")
    
    if not gitignore_file.exists():
        print_warning(".gitignore file not found")
        return False
    
    with open(gitignore_file, 'r') as f:
        content = f.read()
        if ".env" in content:
            print_success(".env is protected in .gitignore ✅")
            return True
        else:
            print_error(".env is NOT in .gitignore")
            return False

def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "🔑 Perplexity API Tester".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    dotenv_ok = check_dotenv()
    gitignore_ok = check_gitignore()
    
    if not dotenv_ok:
        print_error("\n⚠️  Please create .env file first!")
        sys.exit(1)
    
    perplexity_ok = test_perplexity_api()
    
    print_header("Test Summary")
    
    perplexity_status = "✅ Working" if perplexity_ok else "❌ Failed"
    print(f"\nPerplexity API:  {perplexity_status}")
    
    if perplexity_ok:
        print("\n✅ Perplexity is ready to use!")
        print("   You can now run: python src/Phase1_OfflineProcessing/perplexity_enricher.py")
        sys.exit(0)
    else:
        print("\n❌ Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
