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
        '/hardware/uno-rev3',  # Updated to correct UNO R3 URL
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
                
                # For UNO R3, get additional details
                if 'uno-rev3' in board_path:
                    components = extract_uno_components(soup)
                    guides = extract_uno_guides(soup, board_url)
                else:
                    components = []
                    guides = []
                
                device_data = {
                    'DeviceID': i + 1,
                    'DeviceName': device_name,
                    'DeviceType': 'Microcontroller Board',
                    'ImageURL': image_url,
                    'SourceURL': board_url,
                    'components': components,
                    'guides': guides
                }
                
                devices.append(device_data)
                print(f"Found: {device_name}")
                
            time.sleep(1)  # Respect the website
            
        except Exception as e:
            print(f"Error with {board_path}: {e}")
    
    return devices

def extract_uno_components(soup):
    """Extract UNO R3 components and specifications"""
    components = []
    spec_keywords = ['specification', 'feature', 'technical', 'pinout', 'component', 'memory', 'power']
    
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
    for header in headers:
        header_text = header.get_text(strip=True).lower()
        if any(keyword in header_text for keyword in spec_keywords):
            content = header.find_next(['p', 'ul', 'table'])
            if content:
                component_id = len(components) + 1
                components.append({
                    'ComponentID': component_id,
                    'ComponentName': header.get_text(strip=True),
                    'Description': content.get_text(strip=True)[:500]
                })
    
    return components

def extract_uno_guides(soup, board_url):
    """Extract UNO R3 guides and steps"""
    guides = []
    
    # Look for tutorial content in the page
    content_areas = soup.find_all(['article', 'section', 'div'], class_=True)
    
    for i, area in enumerate(content_areas):
        area_text = area.get_text(strip=True)
        if len(area_text) > 200:  # Substantial content
            guide_id = len(guides) + 1
            
            # Create guide title
            guide_title = f"UNO R3 Guide {i+1}"
            title_elem = area.find(['h1', 'h2', 'h3'])
            if title_elem:
                guide_title = title_elem.get_text(strip=True)
            
            guide_data = {
                'GuideID': guide_id,
                'Title': guide_title,
                'DateCreated': datetime.now().strftime('%Y-%m-%d'),
                'GuideURL': board_url,
                'steps': extract_guide_steps(area, guide_id)
            }
            
            guides.append(guide_data)
    
    return guides

def extract_guide_steps(content_area, guide_id):
    """Extract step-by-step instructions from content"""
    steps = []
    
    # Look for ordered lists
    ordered_lists = content_area.find_all('ol')
    for ol in ordered_lists:
        list_items = ol.find_all('li')
        for i, item in enumerate(list_items):
            step_text = item.get_text(strip=True)
            if len(step_text) > 10:
                steps.append({
                    'StepID': len(steps) + 1,
                    'StepNumber': i + 1,
                    'Description': step_text[:300]
                })
    
    # Look for step-like paragraphs
    paragraphs = content_area.find_all('p')
    step_keywords = ['step', 'connect', 'install', 'upload', 'open', 'select', 'plug', 'wire']
    
    for p in paragraphs:
        p_text = p.get_text(strip=True).lower()
        if any(keyword in p_text for keyword in step_keywords) and len(p_text) > 20:
            steps.append({
                'StepID': len(steps) + 1,
                'StepNumber': len(steps) + 1,
                'Description': p.get_text(strip=True)[:300]
            })
    
    return steps

def save_data(devices):
    """Save data to JSON file"""
    os.makedirs('data/raw/scraped_json', exist_ok=True)
    
    # Flatten the data structure for database compatibility
    all_components = []
    all_guides = []
    all_steps = []
    
    for device in devices:
        # Add device ID to components
        for component in device.get('components', []):
            component['DeviceID'] = device['DeviceID']
            all_components.append(component)
        
        # Add device ID to guides and steps
        for guide in device.get('guides', []):
            guide['DeviceID'] = device['DeviceID']
            all_guides.append(guide)
            
            # Add guide ID to steps
            for step in guide.get('steps', []):
                step['GuideID'] = guide['GuideID']
                all_steps.append(step)
    
    data = {
        'devices': devices,
        'components': all_components,
        'guides': all_guides,
        'steps': all_steps
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
        
        # Show UNO R3 details if found
        uno_device = next((device for device in devices if 'uno' in device['DeviceName'].lower()), None)
        if uno_device:
            print(f"\nUNO R3 Details:")
            print(f"Components: {len(uno_device.get('components', []))}")
            print(f"Guides: {len(uno_device.get('guides', []))}")
            total_steps = sum(len(guide.get('steps', [])) for guide in uno_device.get('guides', []))
            print(f"Total Steps: {total_steps}")
    else:
        print("No boards found")

if __name__ == "__main__":
    main()