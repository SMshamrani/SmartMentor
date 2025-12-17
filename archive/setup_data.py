# scripts/setup_data.py

import sys
from pathlib import Path

# إضافة المسار الرئيسي
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# الـ imports الصحيحة
from src.Phase1_OfflineProcessing.data_loader import DataLoader
from src.Phase1_OfflineProcessing.image_downloader_github import GitHubImageDownloader
from src.Phase1_OfflineProcessing.web_scraper_images import ArduinoDocsScraper  # ✅ هذا الخط

def setup_all_data():
    """خطوات تحضير كل البيانات"""
    
    print("=" * 50)
    print("🚀 SmartMentor Data Setup Pipeline")
    print("=" * 50)
    
    try:
        # Step 1: تحميل البيانات المحلية
        print("\n📊 Step 1: Loading local data (XLSX/CSV)...")
        loader = DataLoader()
        data = loader.load_xlsx_csv()
        print("✅ Data loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error in Step 1: {e}")
    
    try:
        # Step 2: تحميل الصور من GitHub
        print("\n🖼️  Step 2: Downloading images from GitHub...")
        github_downloader = GitHubImageDownloader()
        github_downloader.download_all()
        print("✅ Images downloaded!")
        
    except Exception as e:
        print(f"❌ Error in Step 2: {e}")
    
    try:
        # Step 3: كشط الصور من Arduino Docs
        print("\n🕷️  Step 3: Scraping Arduino docs for images...")
        scraper = ArduinoDocsScraper()  # ✅ الآن بيشتغل
        scraper.scrape_getting_started_images()
        print("✅ Docs scraped!")
        
    except Exception as e:
        print(f"❌ Error in Step 3: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("=" * 50)

if __name__ == "__main__":
    setup_all_data()

