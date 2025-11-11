# src/image_downloader.py
from src.utils import download_image
import json
import os
import glob

def download_device_images(json_file_pattern):
    """Download all device images from scraped data"""
    try:
        # Find the latest JSON file
        json_files = glob.glob(json_file_pattern)
        if not json_files:
            print("No JSON files found matching pattern")
            return []
        
        latest_file = max(json_files, key=os.path.getctime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        downloaded_images = []
        
        for device in data['devices']:
            if device.get('ImageURL'):
                filename = f"device_{device['DeviceID']}_{device['DeviceName'].replace(' ', '_')}"
                image_path = download_image(
                    device['ImageURL'], 
                    'data/raw/scraped_images', 
                    filename
                )
                
                if image_path:
                    downloaded_images.append({
                        'device_id': device['DeviceID'],
                        'device_name': device['DeviceName'],
                        'image_path': image_path
                    })
                    print(f"Downloaded image for: {device['DeviceName']}")
        
        print(f"Downloaded {len(downloaded_images)} images")
        return downloaded_images
        
    except Exception as e:
        print(f"Error downloading images: {e}")
        return []