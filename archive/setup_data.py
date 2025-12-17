# scripts/setup_data.py
"""
Data setup pipeline script for the SmartMentor project.
Loads local tabular data and downloads example images from GitHub and Arduino Docs.
"""

import sys
from pathlib import Path

# Add project root to Python path so that src can be imported
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Phase 1 offline processing utilities
from src.Phase1_OfflineProcessing.data_loader import DataLoader
from src.Phase1_OfflineProcessing.image_downloader_github import GitHubImageDownloader
from src.Phase1_OfflineProcessing.web_scraper_images import ArduinoDocsScraper


def setup_all_data():
    """Run all data preparation steps: load data, download images, and scrape docs."""

    print("=" * 50)
    print("SmartMentor Data Setup Pipeline")
    print("=" * 50)

    # Step 1: Load local tabular data (XLSX/CSV)
    try:
        print("\nStep 1: Loading local data (XLSX/CSV)...")
        loader = DataLoader()
        data = loader.load_xlsx_csv()
        print("Data loaded successfully")
    except Exception as e:
        print(f"Error in Step 1 (data loading): {e}")

    # Step 2: Download images from GitHub
    try:
        print("\nStep 2: Downloading images from GitHub...")
        github_downloader = GitHubImageDownloader()
        github_downloader.download_all()
        print("Images downloaded from GitHub")
    except Exception as e:
        print(f"Error in Step 2 (GitHub images): {e}")

    # Step 3: Scrape images from Arduino official documentation
    try:
        print("\nStep 3: Scraping Arduino docs for images...")
        scraper = ArduinoDocsScraper()
        scraper.scrape_getting_started_images()
        print("Arduino docs scraped successfully")
    except Exception as e:
        print(f"Error in Step 3 (Arduino docs scraping): {e}")

    print("\n" + "=" * 50)
    print("Setup complete")
    print("=" * 50)


if __name__ == "__main__":
    setup_all_data()
