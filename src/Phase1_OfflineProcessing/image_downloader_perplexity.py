# src/Phase1_OfflineProcessing/image_downloader_perplexity.py

import requests
import json
from pathlib import Path
from urllib.parse import urljoin

class PerplexityImageDownloader:
    def __init__(self, perplexity_api_key):
        self.api_key = perplexity_api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.image_dir = Path("data/raw/scraped_images/official_docs")
        self.image_dir.mkdir(parents=True, exist_ok=True)
    
    def get_image_urls(self):
        """البحث عن صور Arduino من الإنترنت عبر Perplexity"""
        
        prompt = """
        أريد قائمة بأفضل صور Arduino UNO R3 الموثقة من المصادر الرسمية.
        
        الصور المطلوبة:
        1. Pinout Diagram (الرسم التوضيحي للدبابيس)
        2. Arduino UNO Board (صورة اللوحة الكاملة)
        3. Getting Started Setup (صورة التوصيل الأولي)
        4. LED Connection Example (مثال توصيل LED)
        5. Breadboard Wiring (توصيل بـ Breadboard)
        
        أعطني:
        - اسم الصورة
        - رابط التحميل المباشر
        - الموقع الرسمي (arduino.cc, sparkfun.com, Adafruit, إلخ)
        
        صيغة JSON:
        [
            {
                "name": "pinout_diagram",
                "url": "https://...",
                "source": "arduino.cc",
                "description": "..."
            }
        ]
        """
        
        response = requests.post(
            self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        
        result = response.json()
        return json.loads(result['choices'][0]['message']['content'])
    
    def download_images(self):
        """تحميل الصور"""
        
        image_list = self.get_image_urls()
        
        for image_info in image_list:
            try:
                url = image_info['url']
                filename = image_info['name']
                
                # تحميل الصورة
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    # حفظ الصورة
                    filepath = self.image_dir / f"{filename}.jpg"
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✅ Downloaded: {filename}")
                else:
                    print(f"❌ Failed to download: {filename}")
            
            except Exception as e:
                print(f"⚠️ Error downloading {filename}: {e}")

# استخدام:
downloader = PerplexityImageDownloader(api_key="YOUR_PERPLEXITY_API_KEY")
downloader.download_images()
