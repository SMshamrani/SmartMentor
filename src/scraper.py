import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import urljoin
from datetime import datetime

class ArduinoScraper:
    def __init__(self):
        self.base_url = "https://docs.arduino.cc"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Data structure matching your database schema
        self.data = {
            'devices': [],
            'components': [],
            'guides': [],
            'steps': []
        }
    
    def scrape_arduino_boards(self):
        """Scrape Arduino boards from the hardware section"""
        boards_url = f"{self.base_url}/hardware"
        print(f"Scraping Arduino boards from: {boards_url}")
        
        try:
            response = self.session.get(boards_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find board cards - adjust selectors based on actual website structure
            board_cards = soup.find_all('a', class_='card') or soup.find_all('div', class_='board-item')
            
            for i, card in enumerate(board_cards[:10]):  # First 10 for testing
                board_data = self.extract_board_data(card)
                if board_data:
                    self.data['devices'].append(board_data)
                    print(f"Collected: {board_data['DeviceName']}")
                
                time.sleep(1)  # Respect the website
            
        except Exception as e:
            print(f"Error scraping boards: {e}")
    
    def extract_board_data(self, card):
        """Extract board data from card element"""
        try:
            # Extract board name
            title_elem = card.find('h3') or card.find('h2') or card.find('strong')
            device_name = title_elem.get_text(strip=True) if title_elem else f"Arduino Board {len(self.data['devices'])+1}"
            
            # Extract URL
            link = card.get('href')
            full_url = urljoin(self.base_url, link) if link else ""
            
            # Extract image
            img_elem = card.find('img')
            image_url = ""
            if img_elem and img_elem.get('src'):
                image_url = urljoin(self.base_url, img_elem['src'])
            
            device_id = len(self.data['devices']) + 1
            
            return {
                'DeviceID': device_id,
                'DeviceName': device_name,
                'DeviceType': 'Microcontroller Board',
                'ImageURL': image_url,
                'SourceURL': full_url
            }
            
        except Exception as e:
            print(f"Error extracting board data: {e}")
            return None
    
    def scrape_board_details(self, device_data):
        """Scrape additional details for a board"""
        if not device_data['SourceURL']:
            return
        
        try:
            response = self.session.get(device_data['SourceURL'])
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract components
            components = self.extract_components(soup, device_data['DeviceID'])
            self.data['components'].extend(components)
            
            # Extract guides
            guides = self.extract_guides(soup, device_data['DeviceID'])
            self.data['guides'].extend(guides)
            
            print(f"Collected {len(components)} components and {len(guides)} guides for {device_data['DeviceName']}")
            
        except Exception as e:
            print(f"Error scraping board details: {e}")
    
    def extract_components(self, soup, device_id):
        """Extract board components and specifications"""
        components = []
        
        # Look for component sections
        sections = soup.find_all(['h2', 'h3'], string=['Specifications', 'Features', 'Components', 'Pins', 'Technical'])
        
        for section in sections[:3]:  # First 3 sections only
            content = section.find_next('ul') or section.find_next('p') or section.find_next('div')
            if content:
                component_id = len(self.data['components']) + len(components) + 1
                components.append({
                    'ComponentID': component_id,
                    'DeviceID': device_id,
                    'ComponentName': section.get_text(strip=True),
                    'Description': content.get_text(strip=True)[:500]  # First 500 chars
                })
        
        return components
    
    def extract_guides(self, soup, device_id):
        """Extract guides and tutorials for the board"""
        guides = []
        
        # Find guide links
        guide_links = soup.find_all('a', href=True)
        guide_keywords = ['guide', 'tutorial', 'getting started', 'setup', 'learn']
        
        for link in guide_links:
            link_text = link.get_text(strip=True).lower()
            if any(keyword in link_text for keyword in guide_keywords):
                guide_id = len(self.data['guides']) + len(guides) + 1
                
                guide = {
                    'GuideID': guide_id,
                    'DeviceID': device_id,
                    'Title': link.get_text(strip=True),
                    'DateCreated': datetime.now().strftime('%Y-%m-%d'),
                    'GuideURL': urljoin(self.base_url, link['href'])
                }
                
                guides.append(guide)
                
                # Extract steps for this guide
                steps = self.extract_guide_steps(guide['GuideURL'], guide_id)
                self.data['steps'].extend(steps)
        
        return guides[:5]  # First 5 guides only
    
    def extract_guide_steps(self, guide_url, guide_id):
        """Extract step-by-step instructions from a guide"""
        steps = []
        
        try:
            response = self.session.get(guide_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find numbered steps or list items
            step_elements = soup.find_all('li') or soup.find_all('p')
            
            for i, step in enumerate(step_elements[:15]):  # First 15 steps
                step_text = step.get_text(strip=True)
                # Filter for meaningful steps (not too short, contains action words)
                if len(step_text) > 20 and any(word in step_text.lower() for word in ['connect', 'install', 'upload', 'open', 'select']):
                    steps.append({
                        'StepID': len(self.data['steps']) + len(steps) + 1,
                        'GuideID': guide_id,
                        'StepNumber': i + 1,
                        'Description': step_text[:300]  # First 300 chars
                    })
        
        except Exception as e:
            print(f"Error extracting guide steps: {e}")
        
        return steps
    
    def save_to_json(self):
        """Save scraped data to JSON file"""
        os.makedirs('data/raw/scraped_json', exist_ok=True)
        
        filename = f"data/raw/scraped_json/arduino_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        print(f"Data saved to: {filename}")
        return filename
    
    def run(self):
        """Run the complete scraping process"""
        print("Starting Arduino data collection...")
        
        self.scrape_arduino_boards()
        
        # Get details for each board
        for device in self.data['devices']:
            self.scrape_board_details(device)
            time.sleep(2)  # Delay between requests
        
        # Save data
        self.save_to_json()
        
        print(f"Completed! Results:")
        print(f"   - Devices: {len(self.data['devices'])}")
        print(f"   - Components: {len(self.data['components'])}")
        print(f"   - Guides: {len(self.data['guides'])}")
        print(f"   - Steps: {len(self.data['steps'])}")

def run_scraper():
    scraper = ArduinoScraper()
    scraper.run()

if __name__ == "__main__":
    run_scraper()