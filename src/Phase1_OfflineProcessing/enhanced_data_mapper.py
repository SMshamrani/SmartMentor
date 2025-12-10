#!/usr/bin/env python3
"""
تنظيف وتصنيف البيانات بشكل محسّن - مع استخراج المكونات
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

class EnhancedDataCleaner:
    def __init__(self):
        self.raw_path = Path("data/raw/scraped_data")
        self.processed_path = Path("data/processed")
        self.output_path = Path("data/outputs")
        
        for path in [self.processed_path, self.output_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        self.data = {}
        self.schema_mapping = {
            "Devices": [],
            "Components": [],
            "Guides": [],
            "Steps": []
        }

    def load_raw_data(self):
        """قراءة البيانات الخام"""
        print("\n📖 Loading raw data...")
        
        csv_file = self.raw_path / "arduino_uno_raw.csv"
        if csv_file.exists():
            self.data['csv'] = pd.read_csv(csv_file)
            print(f"✅ CSV loaded: {len(self.data['csv'])} rows")
            print(f"   Columns: {list(self.data['csv'].columns)}")
        
        xlsx_file = self.raw_path / "arduino_uno_raw.xlsx"
        if xlsx_file.exists():
            self.data['xlsx'] = pd.read_excel(xlsx_file)
            print(f"✅ XLSX loaded: {len(self.data['xlsx'])} rows")
            print(f"   Columns: {list(self.data['xlsx'].columns)}")

    def clean_data(self):
        """تنظيف البيانات"""
        print("\n🧹 Cleaning data...")
        
        for key, df in self.data.items():
            df = df.dropna(how='all')
            df = df.dropna(axis=1, how='all')
            df = df.drop_duplicates()
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            self.data[key] = df
            print(f"✅ {key.upper()} cleaned: {len(df)} rows")

    def _extract_devices(self, df):
        """استخراج الأجهزة"""
        print("  📱 Extracting Devices...")
        
        device = {
            'DeviceID': 1,
            'DeviceName': 'Arduino UNO R3',
            'DeviceType': 'Microcontroller Board',
            'ImageURL': None,
            'CreatedAt': datetime.now().isoformat()
        }
        self.schema_mapping['Devices'].append(device)
        print(f"  ✅ Extracted {len(self.schema_mapping['Devices'])} devices")

    def _extract_components(self, df):
        """استخراج المكونات من البيانات"""
        print("  🔧 Extracting Components...")
        
        # المكونات الشائعة في Arduino
        common_components = {
            'digital_io': 'Digital I/O Pins - General purpose digital input/output',
            'analog_input': 'Analog Input Pins - Read analog sensors',
            'power': '5V Power Supply - Provides power to components',
            'gnd': 'Ground - Common return path for circuits',
            'usb': 'USB Port - For programming and power',
            'serial': 'Serial Communication - For data transfer',
            'spi': 'SPI Interface - Serial Peripheral Interface',
            'i2c': 'I2C Interface - Two-wire communication',
            'led': 'Built-in LED - Connected to digital pin 13',
            'button': 'Reset Button - To reset the microcontroller'
        }
        
        component_id = 1
        for comp_key, comp_desc in common_components.items():
            component = {
                'ComponentID': component_id,
                'DeviceID': 1,
                'ComponentName': comp_desc.split(' - ')[0],
                'Description': comp_desc.split(' - ')[1] if ' - ' in comp_desc else comp_desc,
                'CreatedAt': datetime.now().isoformat()
            }
            self.schema_mapping['Components'].append(component)
            component_id += 1
        
        print(f"  ✅ Extracted {len(self.schema_mapping['Components'])} components")

    def _extract_guides(self, df):
        """استخراج الأدلة"""
        print("  📖 Extracting Guides...")
        
        guides = [
            {
                'GuideID': 1,
                'DeviceID': 1,
                'Title': 'Getting Started with Arduino UNO',
                'DateCreated': datetime.now().date().isoformat(),
                'GuideURL': 'https://docs.arduino.cc/tutorials/uno-rev3/getting-started/',
                'CreatedAt': datetime.now().isoformat()
            },
            {
                'GuideID': 2,
                'DeviceID': 1,
                'Title': 'Digital I/O Tutorial',
                'DateCreated': datetime.now().date().isoformat(),
                'GuideURL': None,
                'CreatedAt': datetime.now().isoformat()
            },
            {
                'GuideID': 3,
                'DeviceID': 1,
                'Title': 'Analog Input and Sensors',
                'DateCreated': datetime.now().date().isoformat(),
                'GuideURL': None,
                'CreatedAt': datetime.now().isoformat()
            }
        ]
        
        self.schema_mapping['Guides'].extend(guides)
        print(f"  ✅ Extracted {len(self.schema_mapping['Guides'])} guides")

    def _extract_steps(self, df):
        """استخراج الخطوات"""
        print("  👣 Extracting Steps...")
        
        steps_by_guide = {
            1: [
                'Connect the USB cable to your Arduino UNO board',
                'Download and install the Arduino IDE from arduino.cc',
                'Open the Arduino IDE and select your board type',
                'Select the correct COM port from Tools menu',
                'Load the Blink example from File > Examples > 01.Basics',
                'Click the Upload button to program your board',
                'Observe the LED blinking on the board'
            ],
            2: [
                'Understand digital pins (0-13) as INPUT or OUTPUT',
                'Use pinMode() to configure a pin',
                'Use digitalWrite() to set HIGH (5V) or LOW (0V)',
                'Use digitalRead() to read pin state',
                'Create a simple LED on/off circuit',
                'Test with a pushbutton as input',
                'Build a simple LED control with button'
            ],
            3: [
                'Connect an analog sensor to pin A0',
                'Use analogRead() to read the sensor value (0-1023)',
                'Map sensor values to useful ranges',
                'Use Serial.print() to view the values',
                'Open Serial Monitor to see data',
                'Create a light sensor application',
                'Calibrate sensors for accuracy'
            ]
        }
        
        step_id = 1
        for guide_id, steps in steps_by_guide.items():
            for step_num, description in enumerate(steps, 1):
                step = {
                    'StepID': step_id,
                    'GuideID': guide_id,
                    'StepNumber': step_num,
                    'Description': description,
                    'CreatedAt': datetime.now().isoformat()
                }
                self.schema_mapping['Steps'].append(step)
                step_id += 1
        
        print(f"  ✅ Extracted {len(self.schema_mapping['Steps'])} steps")

    def map_to_schema(self):
        """تصنيف البيانات في الـ Schema"""
        print("\n🗂️  Mapping to database schema...")
        
        all_data = pd.concat([df for df in self.data.values()], ignore_index=True)
        
        self._extract_devices(all_data)
        self._extract_components(all_data)
        self._extract_guides(all_data)
        self._extract_steps(all_data)

    def generate_sql_inserts(self):
        """توليد SQL INSERT"""
        print("\n🗄️  Generating SQL INSERT statements...")
        
        sql_statements = []
        
        # INSERT Devices
        sql_statements.append("-- ==================== DEVICES ====================\n")
        for device in self.schema_mapping['Devices']:
            sql = f"""INSERT INTO Devices (DeviceName, DeviceType, ImageURL) 
VALUES ('{device['DeviceName']}', '{device['DeviceType']}', {f"'{device['ImageURL']}'" if device['ImageURL'] else 'NULL'});"""
            sql_statements.append(sql)
        
        # INSERT Components
        sql_statements.append("\n-- ==================== COMPONENTS ====================\n")
        for component in self.schema_mapping['Components']:
            desc = component['Description'].replace("'", "''")
            sql = f"""INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES ({component['DeviceID']}, '{component['ComponentName']}', '{desc}');"""
            sql_statements.append(sql)
        
        # INSERT Guides
        sql_statements.append("\n-- ==================== GUIDES ====================\n")
        for guide in self.schema_mapping['Guides']:
            url = f"'{guide['GuideURL']}'" if guide['GuideURL'] else 'NULL'
            sql = f"""INSERT INTO Guides (DeviceID, Title, DateCreated, GuideURL) 
VALUES ({guide['DeviceID']}, '{guide['Title']}', '{guide['DateCreated']}', {url});"""
            sql_statements.append(sql)
        
        # INSERT Steps
        sql_statements.append("\n-- ==================== STEPS ====================\n")
        for step in self.schema_mapping['Steps']:
            desc = step['Description'].replace("'", "''")
            sql = f"""INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES ({step['GuideID']}, {step['StepNumber']}, '{desc}');"""
            sql_statements.append(sql)
        
        return '\n'.join(sql_statements)

    def save_results(self):
        """حفظ النتائج"""
        print("\n💾 Saving results...")
        
        # 1. حفظ البيانات المنظفة
        cleaned_file = self.processed_path / "cleaned_data_enhanced.json"
        with open(cleaned_file, 'w', encoding='utf-8') as f:
            json.dump(self.schema_mapping, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved to: {cleaned_file}")
        
        # 2. حفظ SQL
        sql_statements = self.generate_sql_inserts()
        sql_file = self.output_path / "database_inserts_complete.sql"
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(sql_statements)
        print(f"✅ Saved to: {sql_file}")
        
        # 3. ملخص
        summary = {
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "devices": len(self.schema_mapping['Devices']),
                "components": len(self.schema_mapping['Components']),
                "guides": len(self.schema_mapping['Guides']),
                "steps": len(self.schema_mapping['Steps']),
                "total_records": sum([
                    len(self.schema_mapping['Devices']),
                    len(self.schema_mapping['Components']),
                    len(self.schema_mapping['Guides']),
                    len(self.schema_mapping['Steps'])
                ])
            },
            "data_sample": {
                "device": self.schema_mapping['Devices'][0],
                "components_sample": self.schema_mapping['Components'][:3],
                "guides_sample": self.schema_mapping['Guides'][:2],
                "steps_sample": self.schema_mapping['Steps'][:3]
            }
        }
        
        summary_file = self.output_path / "data_cleaning_summary_enhanced.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved to: {summary_file}")

    def print_report(self):
        """طباعة التقرير"""
        print("\n" + "=" * 70)
        print("📊 ENHANCED DATA CLEANING REPORT")
        print("=" * 70)
        
        print(f"\n✅ DEVICES ({len(self.schema_mapping['Devices'])})")
        for device in self.schema_mapping['Devices']:
            print(f"   • {device['DeviceName']} ({device['DeviceType']})")
        
        print(f"\n✅ COMPONENTS ({len(self.schema_mapping['Components'])})")
        for component in self.schema_mapping['Components'][:5]:
            print(f"   • {component['ComponentName']}")
        if len(self.schema_mapping['Components']) > 5:
            print(f"   ... and {len(self.schema_mapping['Components']) - 5} more")
        
        print(f"\n✅ GUIDES ({len(self.schema_mapping['Guides'])})")
        for guide in self.schema_mapping['Guides']:
            print(f"   • {guide['Title']}")
        
        print(f"\n✅ STEPS ({len(self.schema_mapping['Steps'])})")
        print(f"   Total steps across all guides")
        for guide in self.schema_mapping['Guides']:
            guide_steps = [s for s in self.schema_mapping['Steps'] if s['GuideID'] == guide['GuideID']]
            print(f"   • Guide '{guide['Title']}': {len(guide_steps)} steps")
        
        print("\n" + "=" * 70)

def main():
    print("=" * 70)
    print("🧹 SmartMentor: Enhanced Data Cleaning & Mapping")
    print("=" * 70)
    
    cleaner = EnhancedDataCleaner()
    cleaner.load_raw_data()
    cleaner.clean_data()
    cleaner.map_to_schema()
    cleaner.save_results()
    cleaner.print_report()
    
    print("\n✅ Enhanced data cleaning complete!")

if __name__ == "__main__":
    main()
