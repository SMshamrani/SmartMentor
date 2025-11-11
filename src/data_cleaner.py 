# src/data_cleaner.py
import json
import os
import glob
from datetime import datetime

class DataCleaner:
    def __init__(self):
        self.cleaned_data = {
            'devices': [],
            'components': [],
            'guides': [],
            'steps': []
        }
    
    def load_latest_data(self):
        """Load the most recent scraped data file"""
        json_files = glob.glob('data/raw/scraped_json/arduino_data_*.json')
        if not json_files:
            print("No scraped data files found")
            return None
        
        latest_file = max(json_files, key=os.path.getctime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data file: {e}")
            return None
    
    def remove_duplicates(self, data):
        """Remove duplicate entries based on key fields"""
        # Remove duplicate devices
        seen_devices = set()
        for device in data['devices']:
            key = (device['DeviceName'], device['DeviceType'])
            if key not in seen_devices:
                seen_devices.add(key)
                self.cleaned_data['devices'].append(device)
        
        # Remove duplicate components
        seen_components = set()
        for component in data['components']:
            key = (component['DeviceID'], component['ComponentName'])
            if key not in seen_components:
                seen_components.add(key)
                self.cleaned_data['components'].append(component)
        
        # Remove duplicate guides
        seen_guides = set()
        for guide in data['guides']:
            key = (guide['DeviceID'], guide['Title'])
            if key not in seen_guides:
                seen_guides.add(key)
                self.cleaned_data['guides'].append(guide)
        
        # Remove duplicate steps
        seen_steps = set()
        for step in data['steps']:
            key = (step['GuideID'], step['StepNumber'])
            if key not in seen_steps:
                seen_steps.add(key)
                self.cleaned_data['steps'].append(step)
    
    def validate_data(self):
        """Validate data integrity and relationships"""
        # Check foreign key relationships
        device_ids = {device['DeviceID'] for device in self.cleaned_data['devices']}
        
        # Filter components with valid DeviceID
        self.cleaned_data['components'] = [
            comp for comp in self.cleaned_data['components'] 
            if comp['DeviceID'] in device_ids
        ]
        
        # Filter guides with valid DeviceID
        self.cleaned_data['guides'] = [
            guide for guide in self.cleaned_data['guides'] 
            if guide['DeviceID'] in device_ids
        ]
        
        # Filter steps with valid GuideID
        guide_ids = {guide['GuideID'] for guide in self.cleaned_data['guides']}
        self.cleaned_data['steps'] = [
            step for step in self.cleaned_data['steps'] 
            if step['GuideID'] in guide_ids
        ]
    
    def save_cleaned_data(self):
        """Save cleaned data to processed folder"""
        os.makedirs('data/processed/cleaned_data', exist_ok=True)
        
        filename = f"data/processed/cleaned_data/cleaned_arduino_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.cleaned_data, f, ensure_ascii=False, indent=2)
        
        print(f"Cleaned data saved to: {filename}")
        return filename
    
    def run_cleaning(self):
        """Run the complete data cleaning process"""
        print("Starting data cleaning process...")
        
        raw_data = self.load_latest_data()
        if not raw_data:
            return
        
        # Remove duplicates
        self.remove_duplicates(raw_data)
        
        # Validate data relationships
        self.validate_data()
        
        # Save cleaned data
        self.save_cleaned_data()
        
        print(f"Cleaning completed:")
        print(f"   - Devices: {len(self.cleaned_data['devices'])}")
        print(f"   - Components: {len(self.cleaned_data['components'])}")
        print(f"   - Guides: {len(self.cleaned_data['guides'])}")
        print(f"   - Steps: {len(self.cleaned_data['steps'])}")

def clean_data():
    cleaner = DataCleaner()
    cleaner.run_cleaning()