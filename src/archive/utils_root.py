# src/utils.py
import requests
import os

def download_image(url, folder_path, filename):
    """Download image from URL"""
    try:
        if not url.startswith('http'):
            return None
            
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            os.makedirs(folder_path, exist_ok=True)
            
            # Determine image extension
            ext = url.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                ext = 'jpg'
            
            filepath = os.path.join(folder_path, f"{filename}.{ext}")
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filepath
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
    
    return None

def setup_folders():
    """Create required folder structure"""
    folders = [
        'data/raw/scraped_json',
        'data/raw/scraped_images',
        'data/processed/cleaned_data', 
        'data/processed/classified_images'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")