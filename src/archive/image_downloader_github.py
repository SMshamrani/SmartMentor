# src/Phase1_OfflineProcessing/image_downloader_github.py

import requests
from pathlib import Path
import json

class GitHubImageDownloader:
    def __init__(self):
        # روابط GitHub الرسمية للصور
        self.github_urls = {
            "pinout": "https://raw.githubusercontent.com/arduino/ArduinoCore-avr/master/variants/standard/pins_arduino.h",
            "board_image": "https://github.com/arduino/arduino-board-index/raw/main/package_index.json"
        }
        
        self.image_dir = Path("data/raw/scraped_images/official_docs")
        self.image_dir.mkdir(parents=True, exist_ok=True)
    
    def get_arduino_images_from_docs(self):
        """الحصول على الصور من Arduino Official Documentation"""
        
        # 1. صور من Arduino Docs
        docs_images = {
            "pinout_diagram": "https://docs.arduino.cc/static/8d20e34af32d2d5aeaa1ba3d1e6dd89d/b8d4c/Pinout.svg",
            "getting_started": "https://docs.arduino.cc/tutorials/uno-rev3/getting-started/",
        }
        
        # 2. صور من WikiMedia Commons
        wikimedia_images = {
            "arduino_uno_photo": "https://upload.wikimedia.org/wikipedia/commons/3/38/Arduino_Uno_-_R3.jpg",
            "breadboard_setup": "https://upload.wikimedia.org/wikipedia/commons/e/e5/Arduino_Uno_with_Breadboard.png"
        }
        
        return {**docs_images, **wikimedia_images}
    
    def download_all(self):
        """تحميل جميع الصور"""
        
        images = self.get_arduino_images_from_docs()
        
        for name, url in images.items():
            try:
                print(f"⏳ Downloading {name}...")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    # استخراج الامتداد من الرابط
                    ext = url.split('.')[-1].split('?')[0]
                    if ext not in ['jpg', 'png', 'svg']:
                        ext = 'jpg'
                    
                    filepath = self.image_dir / f"{name}.{ext}"
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✅ Downloaded: {filepath}")
                    
            except Exception as e:
                print(f"⚠️ Failed {name}: {e}")

# استخدام:
downloader = GitHubImageDownloader()
downloader.download_all()
