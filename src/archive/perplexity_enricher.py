#!/usr/bin/env python3
"""
استخدام Perplexity API لإثراء البيانات بمعلومات محدثة
"""

import requests
import json
from pathlib import Path
from datetime import datetime
import os
import time
from dotenv import load_dotenv

load_dotenv()

class PerplexityEnricher:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found. Set it in .env file")
        
        self.base_url = "https://api.perplexity.ai/chat/completions"
        # جرب النماذج المختلفة
        self.models_to_try = [
            "llama-2-70b-chat",
            "mistral-7b-instruct",
            "openhermes-2.5-mistral-7b",
            "pplx-7b-chat",
            "pplx-70b-chat"
        ]
        
        self.model = self.find_working_model()
        self.output_path = Path("data/outputs")
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "api_key_status": "configured",
            "model_used": self.model,
            "enriched_components": [],
            "enriched_tutorials": [],
            "total_requests": 0
        }
    
    def find_working_model(self):
        """البحث عن نموذج يعمل"""
        print("\n🔍 Finding working model...")
        
        for model in self.models_to_try:
            print(f"   Testing: {model}...", end=" ")
            try:
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
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
                    return model
                else:
                    print("❌")
            except:
                print("❌")
        
        print(f"\n⚠️  No working model found!")
        print("Using default: llama-2-70b-chat")
        return "llama-2-70b-chat"
    
    def search_component(self, component_name):
        """البحث عن معلومات مكون معين"""
        print(f"\n🔍 Searching for: {component_name}")
        
        prompt = f"""
        أريد معلومات دقيقة عن {component_name} في Arduino UNO:
        
        الرجاء توفير:
        1. الوصف التقني (2-3 جمل)
        2. طريقة التوصيل (Pinout)
        3. جهد التشغيل
        4. التيار الأقصى
        5. مثال كود بسيط
        6. حالات الاستخدام الشائعة
        
        اجعل الإجابة منظمة وواضحة.
        """
        
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            self.results["total_requests"] += 1
            
            if response.status_code == 200:
                data = response.json()
                answer = data['choices'][0]['message']['content']
                
                result = {
                    "component": component_name,
                    "answer": answer,
                    "status": "success"
                }
                
                self.results["enriched_components"].append(result)
                print(f"✅ Found: {component_name}")
                print(f"📝 {answer[:80]}...")
                return result
            else:
                error_result = {
                    "component": component_name,
                    "error": f"API Error {response.status_code}",
                    "status": "failed"
                }
                self.results["enriched_components"].append(error_result)
                print(f"❌ Error {response.status_code}")
                return error_result
        
        except Exception as e:
            error_result = {
                "component": component_name,
                "error": str(e),
                "status": "failed"
            }
            self.results["enriched_components"].append(error_result)
            print(f"❌ Exception: {e}")
            return error_result
    
    def search_tutorial_steps(self, tutorial_title):
        """البحث عن خطوات الدرس"""
        print(f"\n📚 Searching: {tutorial_title}")
        
        prompt = f"""
        أريد خطوات عملية وواضحة لـ: {tutorial_title} مع Arduino UNO
        
        الرجاء توفير:
        1. نظرة عامة على الدرس
        2. المكونات المطلوبة
        3. خطوات التنفيذ (مرقمة ومفصلة)
        4. كود المثال الكامل
        5. نصائح استكشاف الأخطاء
        
        اجعل الخطوات واضحة وسهلة للمبتدئين.
        """
        
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            self.results["total_requests"] += 1
            
            if response.status_code == 200:
                data = response.json()
                answer = data['choices'][0]['message']['content']
                
                result = {
                    "tutorial": tutorial_title,
                    "steps": answer,
                    "status": "success"
                }
                
                self.results["enriched_tutorials"].append(result)
                print(f"✅ Tutorial found: {tutorial_title}")
                print(f"📝 {answer[:80]}...")
                return result
            else:
                error_result = {
                    "tutorial": tutorial_title,
                    "error": f"API Error {response.status_code}",
                    "status": "failed"
                }
                self.results["enriched_tutorials"].append(error_result)
                print(f"❌ Error {response.status_code}")
                return error_result
        
        except Exception as e:
            error_result = {
                "tutorial": tutorial_title,
                "error": str(e),
                "status": "failed"
            }
            self.results["enriched_tutorials"].append(error_result)
            print(f"❌ Exception: {e}")
            return error_result
    
    def enrich_all_data(self):
        """إثراء كل البيانات"""
        print("\n" + "=" * 70)
        print("🤖 Enriching data with Perplexity AI")
        print(f"📊 Using model: {self.model}")
        print("=" * 70)
        
        components = [
            "Digital I/O Pins Arduino UNO",
            "Analog Input Pins Arduino UNO",
            "Arduino UNO USB Port",
            "Arduino Serial Communication",
            "Arduino SPI Interface"
        ]
        
        print("\n🔧 Processing Components...")
        for component in components:
            self.search_component(component)
            time.sleep(1)
        
        tutorials = [
            "Getting Started with Arduino UNO",
            "Arduino Digital I/O Control",
            "Arduino Analog Sensor Reading"
        ]
        
        print("\n📚 Processing Tutorials...")
        for tutorial in tutorials:
            self.search_tutorial_steps(tutorial)
            time.sleep(1)
    
    def save_results(self):
        """حفظ النتائج"""
        output_file = self.output_path / "perplexity_enriched_data.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to: {output_file}")
        return output_file
    
    def print_summary(self):
        """طباعة الملخص"""
        print("\n" + "=" * 70)
        print("📊 PERPLEXITY ENRICHMENT SUMMARY")
        print("=" * 70)
        
        successful_components = [c for c in self.results['enriched_components'] if c['status'] == 'success']
        successful_tutorials = [t for t in self.results['enriched_tutorials'] if t['status'] == 'success']
        
        print(f"\n✅ Components: {len(successful_components)}/{len(self.results['enriched_components'])}")
        for comp in successful_components[:3]:
            print(f"   • {comp['component']}")
        
        print(f"\n✅ Tutorials: {len(successful_tutorials)}/{len(self.results['enriched_tutorials'])}")
        for tut in successful_tutorials[:3]:
            print(f"   • {tut['tutorial']}")
        
        print(f"\n📊 Model: {self.results['model_used']}")
        print(f"📊 Total Requests: {self.results['total_requests']}")
        print("=" * 70)

def main():
    print("=" * 70)
    print("🚀 Perplexity Data Enricher")
    print("=" * 70)
    
    try:
        enricher = PerplexityEnricher()
        enricher.enrich_all_data()
        enricher.save_results()
        enricher.print_summary()
        print("\n✅ Enrichment complete!")
    
    except ValueError as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
