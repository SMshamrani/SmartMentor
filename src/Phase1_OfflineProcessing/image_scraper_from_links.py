#!/usr/bin/env python3
"""
استخراج الصور من روابط المشاريع والموثقة
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
import time
import json

class ArduinoProjectImageScraper:
    def __init__(self):
        self.project_links = [
            {
                "name": "andon_system",
                "url": "https://projecthub.arduino.cc/ibrahim_magdy/basic-andon-system-using-arduino-uno-r3-and-python-5214b0",
                "description": "Andon System using Arduino UNO"
            },
            {
                "name": "rfid_reader",
                "url": "https://projecthub.arduino.cc/ZJH/buono-uno-r3-with-rc522-rfid-reader-kit-for-makers-ee12fb",
                "description": "UNO R3 with RFID Reader"
            },
            {
                "name": "blinking_led",
                "url": "https://projecthub.arduino.cc/arohansenroy/blinking-led-77a79f",
                "description": "Blinking LED Tutorial"
            }
        ]
        
        self.document_links = [
            {
                "name": "pinout_diagram",
                "url": "https://docs.arduino.cc/resources/pinouts/A000066-full-pinout.pdf",
                "type": "PDF"
            },
            {
                "name": "datasheet",
                "url": "https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf",
                "type": "PDF"
            },
            {
                "name": "schematics",
                "url": "https://docs.arduino.cc/resources/schematics/A000066-schematics.pdf",
                "type": "PDF"
            }
        ]
        
        self.image_dir = Path("data/raw/scraped_images/project_examples")
        self.image_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "timestamp": str(time.time()),
            "images_downloaded": [],
            "pdfs_downloaded": [],
            "failed_downloads": [],
            "project_info": []
        }

    def scrape_project_images(self):
        """استخراج الصور من مشاريع Arduino Hub"""
        print("\n🔍 Scraping Arduino Project Hub for images...")
        
        for project in self.project_links:
            print(f"\n  📌 Project: {project['name']}")
            print(f"  URL: {project['url']}")
            
            try:
                response = requests.get(project['url'], timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # البحث عن الصور
                images = soup.find_all('img')
                print(f"  🖼️  Found {len(images)} images")
                
                project_images = []
                for idx, img in enumerate(images[:10]):  # أول 10 صور فقط
                    img_url = img.get('src')
                    img_alt = img.get('alt', f'{project["name"]}_image_{idx}')
                    
                    if img_url:
                        # تحويل URL نسبي إلى مطلق
                        if not img_url.startswith('http'):
                            img_url = urljoin(project['url'], img_url)
                        
                        # تحميل الصورة
                        success = self.download_image(img_url, img_alt, project['name'])
                        if success:
                            project_images.append({
                                'name': img_alt,
                                'url': img_url,
                                'project': project['name']
                            })
                        
                        time.sleep(0.3)
                
                # حفظ معلومات المشروع
                self.results["project_info"].append({
                    "project": project['name'],
                    "title": project['description'],
                    "url": project['url'],
                    "images_found": len(project_images)
                })
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.results["failed_downloads"].append({
                    "project": project['name'],
                    "error": str(e)
                })

    def download_pdfs(self):
        """تحميل PDFs من الموثقة الرسمية"""
        print("\n📄 Downloading Arduino documentation PDFs...")
        
        for doc in self.document_links:
            print(f"\n  📥 {doc['name']}")
            
            try:
                response = requests.get(doc['url'], timeout=10)
                
                if response.status_code == 200:
                    filename = self.image_dir / f"{doc['name']}.pdf"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"  ✅ Saved: {filename}")
                    self.results["pdfs_downloaded"].append({
                        "name": doc['name'],
                        "file": str(filename),
                        "size": len(response.content)
                    })
                else:
                    print(f"  ❌ Failed (status {response.status_code})")
                    self.results["failed_downloads"].append({
                        "doc": doc['name'],
                        "status": response.status_code
                    })
                
                time.sleep(0.5)
            
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.results["failed_downloads"].append({
                    "doc": doc['name'],
                    "error": str(e)
                })

    def download_image(self, url, filename, project_name):
        """تحميل صورة واحدة"""
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # استخراج الامتداد
                ext = url.split('.')[-1].split('?')[0]
                if ext not in ['jpg', 'png', 'gif', 'svg', 'webp']:
                    ext = 'jpg'
                
                # تنظيف اسم الملف
                clean_name = "".join(c for c in filename if c.isalnum() or c in '-_')
                filepath = self.image_dir / f"{project_name}_{clean_name}.{ext}"
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"    ✅ {clean_name}")
                self.results["images_downloaded"].append({
                    "name": clean_name,
                    "project": project_name,
                    "file": str(filepath),
                    "size": len(response.content)
                })
                
                return True
            
            return False
        
        except Exception as e:
            print(f"    ❌ {filename}: {e}")
            return False

    def generate_report(self):
        """توليد تقرير"""
        print("\n" + "=" * 70)
        print("📊 IMAGE SCRAPING REPORT")
        print("=" * 70)
        
        print(f"\n✅ IMAGES DOWNLOADED: {len(self.results['images_downloaded'])}")
        for img in self.results['images_downloaded'][:5]:
            print(f"   • {img['project']}: {img['name']}")
        if len(self.results['images_downloaded']) > 5:
            print(f"   ... and {len(self.results['images_downloaded']) - 5} more")
        
        print(f"\n📄 PDFS DOWNLOADED: {len(self.results['pdfs_downloaded'])}")
        for pdf in self.results['pdfs_downloaded']:
            size_kb = pdf['size'] / 1024
            print(f"   • {pdf['name']} ({size_kb:.1f} KB)")
        
        print(f"\n❌ FAILED: {len(self.results['failed_downloads'])}")
        for fail in self.results['failed_downloads'][:3]:
            print(f"   • {fail}")
        
        print(f"\n📌 PROJECTS: {len(self.results['project_info'])}")
        for proj in self.results['project_info']:
            print(f"   • {proj['project']}: {proj['images_found']} images")
        
        print("\n" + "=" * 70)

    def save_results(self):
        """حفظ النتائج"""
        output_file = Path("data/outputs/image_scraping_report.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Report saved to: {output_file}")

def main():
    print("=" * 70)
    print("🔍 Arduino Project Image Scraper")
    print("=" * 70)
    
    scraper = ArduinoProjectImageScraper()
    
    # جمع الصور من المشاريع
    scraper.scrape_project_images()
    
    # تحميل PDFs
    scraper.download_pdfs()
    
    # التقرير
    scraper.generate_report()
    
    # حفظ النتائج
    scraper.save_results()
    
    print("\n✅ Image scraping complete!")

if __name__ == "__main__":
    main()
