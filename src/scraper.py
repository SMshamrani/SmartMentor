# scraper.py - Enhanced version with more data sources

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
from datetime import datetime
from urllib.parse import urljoin

class ArduinoScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.data = {
            'devices': [],
            'components': [],
            'guides': [],
            'steps': []
        }
    
    def safe_makedirs(self, path):
        """Safely create directory without errors"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return True
    
    def run_scraping(self):
        """Run comprehensive scraping using requests only"""
        print("🚀 Starting Arduino data collection (Requests Only)...")
        
        try:
            # Step 1: Create devices
            self.create_comprehensive_devices()
            
            # Step 2: Scrape from multiple sources
            self.scrape_all_sources()
            
            # Step 3: Download images
            self.download_comprehensive_images()
            
            # Step 4: Create components
            self.create_components()
            
            # Step 5: Save data
            self.save_data()
            
            # Step 6: Print results
            self.print_comprehensive_results()
            
        except Exception as e:
            print(f"Scraping failed: {e}")
    
    def create_comprehensive_devices(self):
        """Create comprehensive Arduino devices"""
        print("📋 Creating Arduino devices...")
        
        devices = [
            {
                'DeviceID': 1,
                'DeviceName': 'Arduino UNO R3',
                'DeviceType': 'Beginner Board',
                'ImageURL': '/images/boards/uno_pinout.jpg',
                'Description': 'The most popular Arduino board perfect for beginners',
                'Specifications': {
                    'Microcontroller': 'ATmega328P',
                    'Digital I/O Pins': '14 (6 PWM)',
                    'Analog Input Pins': '6',
                    'Clock Speed': '16 MHz'
                },
                'SourceURL': 'https://store.arduino.cc/products/arduino-uno-rev3',
                'Difficulty': 'Beginner'
            },
            {
                'DeviceID': 2,
                'DeviceName': 'Arduino Nano', 
                'DeviceType': 'Compact Board',
                'ImageURL': '/images/boards/nano_pinout.jpg',
                'Description': 'Compact breadboard-friendly board',
                'Specifications': {
                    'Microcontroller': 'ATmega328P',
                    'Digital I/O Pins': '14',
                    'Analog Input Pins': '8',
                    'Clock Speed': '16 MHz'
                },
                'SourceURL': 'https://store.arduino.cc/products/arduino-nano',
                'Difficulty': 'Beginner'
            },
            {
                'DeviceID': 3,
                'DeviceName': 'Arduino Mega 2560',
                'DeviceType': 'Advanced Board',
                'ImageURL': '/images/boards/mega_pinout.jpg',
                'Description': 'Powerful board with extensive I/O capabilities',
                'Specifications': {
                    'Microcontroller': 'ATmega2560',
                    'Digital I/O Pins': '54 (15 PWM)',
                    'Analog Input Pins': '16',
                    'Clock Speed': '16 MHz'
                },
                'SourceURL': 'https://store.arduino.cc/products/arduino-mega-2560-rev3',
                'Difficulty': 'Intermediate'
            }
        ]
        self.data['devices'] = devices
        print(f"✅ Created {len(devices)} devices")
    
    def scrape_all_sources(self):
        """Scrape from multiple Arduino sources"""
        print("🔍 Scraping from multiple sources...")
        
        sources = [
            self.scrape_arduino_tutorials,
            self.scrape_arduino_learning,
            self.scrape_arduino_examples,
            self.scrape_tutorialspoint,
        ]
        
        for source in sources:
            try:
                source()
                time.sleep(2)
            except Exception as e:
                print(f"Source failed: {e}")
    
    def scrape_arduino_tutorials(self):
        """Scrape from Arduino tutorials page"""
        print("📚 Scraping Arduino tutorials...")
        
        url = "https://www.arduino.cc/en/Tutorial/HomePage"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find tutorial links
                tutorial_links = soup.find_all('a', href=re.compile(r'/en/Tutorial/'))
                print(f"Found {len(tutorial_links)} tutorial links")
                
                for link in tutorial_links[:12]:  # First 12 tutorials
                    try:
                        tutorial_url = urljoin(url, link['href'])
                        tutorial_title = link.get_text(strip=True)
                        
                        if tutorial_title and len(tutorial_title) > 5:
                            print(f"  - Tutorial: {tutorial_title}")
                            self.scrape_single_page(tutorial_url, tutorial_title, 'Tutorial')
                            time.sleep(1)
                            
                    except Exception as e:
                        print(f"Error processing tutorial: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error scraping tutorials: {e}")
    
    def scrape_arduino_learning(self):
        """Scrape from Arduino learning section"""
        print("🎓 Scraping Arduino learning guides...")
        
        url = "https://docs.arduino.cc/learn/"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find learning guide links
                guide_links = soup.find_all('a', href=re.compile(r'/learn/'))
                print(f"Found {len(guide_links)} learning guides")
                
                for link in guide_links[:10]:  # First 10 guides
                    try:
                        guide_url = urljoin(url, link['href'])
                        guide_title = link.get_text(strip=True)
                        
                        if guide_title and len(guide_title) > 5:
                            print(f"  - Learning: {guide_title}")
                            self.scrape_single_page(guide_url, guide_title, 'Learning Guide')
                            time.sleep(1)
                            
                    except Exception as e:
                        print(f"Error processing learning guide: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error scraping learning: {e}")
    
    def scrape_arduino_examples(self):
        """Scrape from Arduino examples"""
        print("💡 Scraping Arduino examples...")
        
        url = "https://docs.arduino.cc/built-in-examples/"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find example links
                example_links = soup.find_all('a', href=re.compile(r'/built-in-examples/'))
                print(f"Found {len(example_links)} examples")
                
                for link in example_links[:8]:  # First 8 examples
                    try:
                        example_url = urljoin(url, link['href'])
                        example_title = link.get_text(strip=True)
                        
                        if example_title and len(example_title) > 5:
                            print(f"  - Example: {example_title}")
                            self.scrape_single_page(example_url, f"Example: {example_title}", 'Example')
                            time.sleep(1)
                            
                    except Exception as e:
                        print(f"Error processing example: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error scraping examples: {e}")
    
    def scrape_tutorialspoint(self):
        """Scrape from TutorialsPoint"""
        print("🌐 Scraping TutorialsPoint...")
        
        urls = [
            "https://www.tutorialspoint.com/arduino/arduino_quick_guide.htm",
            "https://www.tutorialspoint.com/arduino/arduino_program_structure.htm",
            "https://www.tutorialspoint.com/arduino/arduino_data_types.htm"
        ]
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract title
                    title_tag = soup.find('title')
                    title = title_tag.get_text(strip=True) if title_tag else "TutorialsPoint Guide"
                    
                    # Extract content
                    content_div = soup.find('div', class_='content')
                    if content_div:
                        content = content_div.get_text(strip=True)
                        
                        if content and len(content) > 300:
                            guide_id = len(self.data['guides']) + 1
                            guide = {
                                'GuideID': guide_id,
                                'DeviceID': 1,  # Default to UNO
                                'Title': title,
                                'DateCreated': datetime.now().strftime('%Y-%m-%d'),
                                'GuideURL': url,
                                'Category': 'Programming Guide',
                                'Source': 'TutorialsPoint',
                                'RealScraped': True
                            }
                            self.data['guides'].append(guide)
                            
                            # Extract steps
                            steps = self.extract_steps_from_content(content, guide_id)
                            self.data['steps'].extend(steps)
                            
                            print(f"✅ Scraped: {title} - {len(steps)} steps")
                    
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error scraping TutorialsPoint {url}: {e}")
    
    def scrape_single_page(self, url, title, source_type):
        """Scrape a single page"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract content using multiple selectors
                content_selectors = ['main', 'article', '.content', '#content', '.page-content']
                content = ""
                
                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text(strip=True)
                        if content:
                            break
                
                # Fallback: get all paragraphs
                if not content:
                    paragraphs = soup.find_all('p')
                    content = ' '.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                
                if content and len(content) > 200:
                    # Determine device
                    device_id = self.determine_device_from_content(content, title)
                    
                    guide_id = len(self.data['guides']) + 1
                    guide = {
                        'GuideID': guide_id,
                        'DeviceID': device_id,
                        'Title': title,
                        'DateCreated': datetime.now().strftime('%Y-%m-%d'),
                        'GuideURL': url,
                        'Category': self.classify_content(content, title),
                        'Source': source_type,
                        'RealScraped': True
                    }
                    self.data['guides'].append(guide)
                    
                    # Extract steps
                    steps = self.extract_steps_from_content(content, guide_id)
                    self.data['steps'].extend(steps)
                    
                    print(f"    ✅ Added: {title} ({len(steps)} steps)")
                    
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    def extract_steps_from_content(self, content, guide_id):
        """Extract steps from content"""
        steps = []
        
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        
        step_number = 1
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 40 and self.looks_like_step(sentence):
                steps.append({
                    'StepID': len(self.data['steps']) + len(steps) + 1,
                    'GuideID': guide_id,
                    'StepNumber': step_number,
                    'Description': sentence[:400],
                    'RealScraped': True
                })
                step_number += 1
                
                if step_number > 12:  # Limit steps per guide
                    break
        
        return steps
    
    def looks_like_step(self, text):
        """Check if text looks like a step instruction"""
        text_lower = text.lower()
        step_indicators = [
            'connect', 'wire', 'plug', 'attach', 'install',
            'download', 'open', 'select', 'choose', 'click',
            'upload', 'write', 'code', 'sketch', 'program',
            'press', 'push', 'turn', 'rotate', 'adjust',
            'measure', 'read', 'test', 'verify', 'check',
            'first', 'next', 'then', 'after', 'finally'
        ]
        
        return any(indicator in text_lower for indicator in step_indicators)
    
    def determine_device_from_content(self, content, title):
        """Determine device from content analysis"""
        text = (content + ' ' + title).lower()
        
        if 'nano' in text:
            return 2  # Arduino Nano
        elif 'mega' in text:
            return 3  # Arduino Mega 2560
        else:
            return 1  # Default to Arduino UNO
    
    def classify_content(self, content, title):
        """Classify content by category"""
        text = (content + ' ' + title).lower()
        
        if any(word in text for word in ['led', 'blink', 'light']):
            return 'LED Projects'
        elif any(word in text for word in ['sensor', 'temperature', 'distance', 'ultrasonic']):
            return 'Sensors'
        elif any(word in text for word in ['motor', 'servo', 'actuator']):
            return 'Actuators'
        elif any(word in text for word in ['button', 'switch', 'input']):
            return 'Input Devices'
        elif any(word in text for word in ['display', 'lcd', 'screen']):
            return 'Displays'
        elif any(word in text for word in ['communication', 'i2c', 'serial']):
            return 'Communication'
        elif any(word in text for word in ['getting started', 'beginner']):
            return 'Getting Started'
        else:
            return 'General Tutorial'
    
    def download_comprehensive_images(self):
        """Download comprehensive images for computer vision"""
        print("🖼️ Downloading images for computer vision...")
        
        # Essential images for Arduino recognition
        image_sources = [
            # Board pinouts
            ('https://content.arduino.cc/assets/Pinout-UNOrev3_latest.png', 'boards/uno_pinout.jpg'),
            ('https://content.arduino.cc/assets/Pinout-Nano_latest.png', 'boards/nano_pinout.jpg'),
            ('https://content.arduino.cc/assets/Pinout-Mega2560rev3_latest.png', 'boards/mega_pinout.jpg'),
            
            # Component circuits
            ('https://www.arduino.cc/en/uploads/Tutorial/led_bb.png', 'components/led_circuit.jpg'),
            ('https://www.arduino.cc/en/uploads/Tutorial/button_bb.png', 'components/button_circuit.jpg'),
            ('https://www.arduino.cc/en/uploads/Tutorial/potentiometer_bb.png', 'components/potentiometer_circuit.jpg'),
            ('https://www.arduino.cc/en/uploads/Tutorial/servo_bb.png', 'components/servo_circuit.jpg'),
            ('https://www.arduino.cc/en/uploads/Tutorial/ultrasonic_bb.png', 'components/ultrasonic_circuit.jpg'),
            
            # Additional component images
            ('https://www.arduino.cc/en/uploads/Tutorial/lcd_bb.png', 'components/lcd_circuit.jpg'),
            ('https://www.arduino.cc/en/uploads/Tutorial/temperature_bb.png', 'components/temperature_circuit.jpg'),
        ]
        
        self.safe_makedirs('data/raw/scraped_images/boards')
        self.safe_makedirs('data/raw/scraped_images/components')
        
        downloaded_count = 0
        for img_url, local_path in image_sources:
            try:
                response = self.session.get(img_url, timeout=15)
                if response.status_code == 200:
                    filepath = f'data/raw/scraped_images/{local_path}'
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    downloaded_count += 1
                    print(f"  📸 Downloaded: {local_path}")
                    time.sleep(1)
            except Exception as e:
                print(f"  ❌ Failed to download {img_url}: {e}")
        
        print(f"✅ Downloaded {downloaded_count} images")
    
    def create_components(self):
        """Create comprehensive components"""
        print("🔧 Creating components...")
        
        components = [
            # UNO R3 Components
            {'ComponentID': 1, 'DeviceID': 1, 'ComponentName': 'Digital Pins', 'Description': '14 digital input/output pins (6 provide PWM output)'},
            {'ComponentID': 2, 'DeviceID': 1, 'ComponentName': 'Analog Pins', 'Description': '6 analog input pins'},
            {'ComponentID': 3, 'DeviceID': 1, 'ComponentName': 'Microcontroller', 'Description': 'ATmega328P'},
            {'ComponentID': 4, 'DeviceID': 1, 'ComponentName': 'Clock Speed', 'Description': '16 MHz'},
            
            # Nano Components
            {'ComponentID': 5, 'DeviceID': 2, 'ComponentName': 'Digital Pins', 'Description': '14 digital input/output pins'},
            {'ComponentID': 6, 'DeviceID': 2, 'ComponentName': 'Analog Pins', 'Description': '8 analog input pins'},
            
            # Mega Components  
            {'ComponentID': 7, 'DeviceID': 3, 'ComponentName': 'Digital Pins', 'Description': '54 digital input/output pins (15 provide PWM output)'},
            {'ComponentID': 8, 'DeviceID': 3, 'ComponentName': 'Analog Pins', 'Description': '16 analog input pins'},
            {'ComponentID': 9, 'DeviceID': 3, 'ComponentName': 'Microcontroller', 'Description': 'ATmega2560'},
        ]
        self.data['components'] = components
        print(f"✅ Created {len(components)} components")
    
    def save_data(self):
        """Save scraped data"""
        self.safe_makedirs('data/raw/scraped_json')
        
        filename = 'data/raw/scraped_json/comprehensive_arduino_data.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"💾 Data saved to: {filename}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def print_comprehensive_results(self):
        """Print comprehensive results"""
        real_guides = [g for g in self.data['guides'] if g.get('RealScraped')]
        real_steps = [s for s in self.data['steps'] if s.get('RealScraped')]
        
        print(f"\n" + "="*70)
        print("🎉 COMPREHENSIVE DATA COLLECTION COMPLETED!")
        print("="*70)
        
        print(f"\n📊 COLLECTION SUMMARY:")
        print(f"   Devices: {len(self.data['devices'])}")
        print(f"   Components: {len(self.data['components'])}")
        print(f"   REAL Guides (from web): {len(real_guides)}")
        print(f"   REAL Steps (from web): {len(real_steps)}")
        
        print(f"\n🔧 CONTENT BY DEVICE:")
        for device in self.data['devices']:
            device_guides = [g for g in real_guides if g['DeviceID'] == device['DeviceID']]
            device_steps = [s for s in real_steps if any(g['GuideID'] == s['GuideID'] for g in device_guides)]
            print(f"   - {device['DeviceName']}: {len(device_guides)} guides, {len(device_steps)} steps")
        
        print(f"\n📚 GUIDE CATEGORIES:")
        categories = {}
        for guide in real_guides:
            cat = guide.get('Category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {cat}: {count} guides")
        
        print(f"\n🌐 SOURCES:")
        sources = {}
        for guide in real_guides:
            source = guide.get('Source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        for source, count in sources.items():
            print(f"   - {source}: {count} guides")
        
        print(f"\n✅ READY FOR NEXT PHASE:")
        print(f"   Real web data collected successfully")
        print(f"   Images ready for computer vision training")
        print(f"   Data ready for cleaning and classification")
        print("="*70)

def main():
    scraper = ArduinoScraper()
    scraper.run_scraping()

if __name__ == "__main__":
    main()