# simple_scraper.py - Single comprehensive code
import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import urljoin
from datetime import datetime

def scrape_arduino_boards():
    """Scrape Arduino boards data directly"""
    print("Starting Arduino board scraping...")
    
    base_url = "https://docs.arduino.cc"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    devices = []
    
    # Direct links to known Arduino boards
    board_urls = [
        '/hardware/uno-r4',
        '/hardware/uno-r3', 
        '/hardware/nano',
        '/hardware/mega-2560',
        '/hardware/leonardo',
        '/hardware/due',
        '/hardware/micro',
    ]
    
    for i, board_path in enumerate(board_urls):
        try:
            board_url = urljoin(base_url, board_path)
            print(f"Scraping: {board_url}")
            
            response = session.get(board_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract board name
                title = soup.find('h1')
                device_name = title.get_text(strip=True) if title else f"Arduino {board_path.split('/')[-1]}"
                
                # Extract image
                img = soup.find('img')
                image_url = ""
                if img and img.get('src'):
                    image_url = urljoin(base_url, img['src'])
                
                devices.append({
                    'DeviceID': i + 1,
                    'DeviceName': device_name,
                    'DeviceType': 'Microcontroller Board',
                    'ImageURL': image_url,
                    'SourceURL': board_url
                })
                
                print(f"Found: {device_name}")
                
            time.sleep(1)  # Respect the website
            
        except Exception as e:
            print(f"Error with {board_path}: {e}")
    
    return devices

def save_data(devices):
    """Save data to JSON file"""
    os.makedirs('data/raw/scraped_json', exist_ok=True)
    
    data = {
        'devices': devices,
        'components': [],
        'guides': [],
        'steps': []
    }
    
    filename = f"data/raw/scraped_json/arduino_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Data saved to: {filename}")
    return filename

def clean_data(input_file):
    """Simple data cleaning"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Remove devices without images
        data['devices'] = [device for device in data['devices'] if device.get('ImageURL')]
        
        # Save cleaned version
        clean_file = input_file.replace('raw', 'processed/cleaned_data')
        os.makedirs(os.path.dirname(clean_file), exist_ok=True)
        
        with open(clean_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Cleaned data saved to: {clean_file}")
        return clean_file
        
    except Exception as e:
        print(f"Error cleaning data: {e}")
        return None

def download_images(data_file):
    """Download device images"""
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        os.makedirs('data/raw/scraped_images', exist_ok=True)
        downloaded_count = 0
        
        for device in data['devices']:
            if device.get('ImageURL'):
                try:
                    response = requests.get(device['ImageURL'], timeout=10)
                    if response.status_code == 200:
                        # Get file extension
                        ext = device['ImageURL'].split('.')[-1].lower()
                        if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                            ext = 'jpg'
                        
                        filename = f"device_{device['DeviceID']}_{device['DeviceName'].replace(' ', '_')}.{ext}"
                        filepath = os.path.join('data/raw/scraped_images', filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        downloaded_count += 1
                        print(f"Downloaded image: {filename}")
                        
                except Exception as e:
                    print(f"Error downloading image for {device['DeviceName']}: {e}")
        
        print(f"Downloaded {downloaded_count} images")
        
    except Exception as e:
        print(f"Error in download_images: {e}")

def main():
    """Main function"""
    print("Arduino Data Scraper")
    print("=" * 30)
    
    # Create folders
    os.makedirs('data/raw/scraped_json', exist_ok=True)
    os.makedirs('data/raw/scraped_images', exist_ok=True)
    os.makedirs('data/processed/cleaned_data', exist_ok=True)
    
    # Scrape data
    devices = scrape_arduino_boards()
    
    if devices:
        # Save raw data
        data_file = save_data(devices)
        
        # Clean data
        clean_file = clean_data(data_file)
        
        # Download images
        download_images(data_file)
        
        print(f"Completed! Found {len(devices)} boards")
        print("Boards found:")
        for device in devices:
            print(f"  - {device['DeviceName']}")
    else:
        print("No boards found")

if __name__ == "__main__":
    main()