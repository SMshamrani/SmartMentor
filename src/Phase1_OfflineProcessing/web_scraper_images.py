# src/Phase1_OfflineProcessing/web_scraper_images.py

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
import time

class ArduinoDocsScraper:
    def __init__(self):
        self.base_url = "https://docs.arduino.cc"
        self.tutorial_url = "https://docs.arduino.cc/tutorials/uno-rev3/getting-started/"
        self.image_dir = Path("data/raw/scraped_images/official_docs")
        self.image_dir.mkdir(parents=True, exist_ok=True)
    
    def scrape_getting_started_images(self):
        """كشط الصور من صفحة Getting Started"""
        
        try:
            # جلب الصفحة
            response = requests.get(self.tutorial_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # البحث عن جميع الصور
            images = soup.find_all('img')
            
            print(f"🔍 Found {len(images)} images")
            
            for idx, img in enumerate(images):
                try:
                    img_url = img.get('src')
                    img_alt = img.get('alt', f'image_{idx}')
                    
                    # تحويل URL نسبي إلى مطلق
                    if img_url:
                        if img_url.startswith('http'):
                            full_url = img_url
                        else:
                            full_url = urljoin(self.base_url, img_url)
                        
                        # تحميل الصورة
                        self.download_image(full_url, img_alt)
                        time.sleep(0.5)  # تأخير بين التحميلات
                
                except Exception as e:
                    print(f"⚠️ Error with image {idx}: {e}")
        
        except Exception as e:
            print(f"❌ Failed to scrape: {e}")
    
    def download_image(self, url, filename):
        """تحميل صورة واحدة"""
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # استخراج الامتداد
                ext = url.split('.')[-1].split('?')[0]
                if ext not in ['jpg', 'png', 'gif', 'svg']:
                    ext = 'jpg'
                
                # تنظيف اسم الملف
                clean_filename = "".join(c for c in filename if c.isalnum() or c in '-_')
                
                filepath = self.image_dir / f"{clean_filename}.{ext}"
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Saved: {filepath}")
        
        except Exception as e:
            print(f"⚠️ Download failed: {e}")

# استخدام:
scraper = ArduinoDocsScraper()
scraper.scrape_getting_started_images()
