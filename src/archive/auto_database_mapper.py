#!/usr/bin/env python3
"""
تنظيف وتصنيف البيانات تلقائياً في جداول الـ Database
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import re

class DataCleaner:
    def __init__(self):
        self.raw_path = Path("data/raw/scraped_data")
        self.processed_path = Path("data/processed")
        self.output_path = Path("data/outputs")
        
        # إنشاء المجلدات
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
        """قراءة البيانات الخام من CSV و XLSX"""
        print("\n📖 Loading raw data...")
        
        # قراءة CSV
        csv_file = self.raw_path / "arduino_uno_raw.csv"
        if csv_file.exists():
            self.data['csv'] = pd.read_csv(csv_file)
            print(f"✅ CSV loaded: {len(self.data['csv'])} rows")
        
        # قراءة XLSX
        xlsx_file = self.raw_path / "arduino_uno_raw.xlsx"
        if xlsx_file.exists():
            self.data['xlsx'] = pd.read_excel(xlsx_file)
            print(f"✅ XLSX loaded: {len(self.data['xlsx'])} rows")
        
        return self.data

    def clean_data(self):
        """تنظيف البيانات"""
        print("\n🧹 Cleaning data...")
        
        for key, df in self.data.items():
            # حذف الصفوف الفارغة
            df = df.dropna(how='all')
            
            # حذف الأعمدة الفارغة بالكامل
            df = df.dropna(axis=1, how='all')
            
            # حذف النسخ المكررة
            df = df.drop_duplicates()
            
            # تنظيف المسافات الزائدة
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            
            # إعادة تسمية الأعمدة
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            self.data[key] = df
            print(f"✅ {key.upper()} cleaned: {len(df)} rows remain")
        
        return self.data

    def map_to_schema(self):
        """تصنيف البيانات في جداول الـ Schema"""
        print("\n🗂️  Mapping to database schema...")
        
        # الجمع بين البيانات
        all_data = pd.concat([df for df in self.data.values()], ignore_index=True)
        
        # 1. تصنيف الأجهزة (Devices)
        self._extract_devices(all_data)
        
        # 2. تصنيف المكونات (Components)
        self._extract_components(all_data)
        
        # 3. تصنيف الأدلة (Guides)
        self._extract_guides(all_data)
        
        # 4. تصنيف الخطوات (Steps)
        self._extract_steps(all_data)
        
        return self.schema_mapping

    def _extract_devices(self, df):
        """استخراج بيانات الأجهزة"""
        print("  📱 Extracting Devices...")
        
        # البحث عن أسماء الأجهزة
        device_keywords = ['device', 'board', 'arduino', 'name']
        device_cols = [col for col in df.columns if any(kw in col for kw in device_keywords)]
        
        if device_cols:
            devices = df[device_cols].drop_duplicates()
        else:
            # إذا ما في أعمدة واضحة، استخرج من البيانات يدوياً
            devices = pd.DataFrame({
                'device_name': ['Arduino UNO R3'],
                'device_type': ['Microcontroller Board']
            })
        
        for idx, row in devices.iterrows():
            device = {
                'DeviceID': idx + 1,
                'DeviceName': str(row.iloc[0] if len(row) > 0 else 'Arduino UNO'),
                'DeviceType': 'Microcontroller Board',
                'ImageURL': None,
                'CreatedAt': datetime.now().isoformat()
            }
            self.schema_mapping['Devices'].append(device)
        
        print(f"  ✅ Extracted {len(self.schema_mapping['Devices'])} devices")

    def _extract_components(self, df):
        """استخراج بيانات المكونات"""
        print("  🔧 Extracting Components...")
        
        # البحث عن أعمدة المكونات
        component_keywords = ['component', 'pin', 'voltage', 'current', 'type']
        component_cols = [col for col in df.columns if any(kw in col for kw in component_keywords)]
        
        if component_cols:
            components_df = df[component_cols].drop_duplicates()
            
            for idx, row in components_df.iterrows():
                component = {
                    'ComponentID': idx + 1,
                    'DeviceID': 1,  # نفترض أول جهاز
                    'ComponentName': str(row.iloc[0] if len(row) > 0 else f'Component_{idx}'),
                    'Description': ' | '.join(str(val) for val in row.iloc[1:] if pd.notna(val)),
                    'CreatedAt': datetime.now().isoformat()
                }
                self.schema_mapping['Components'].append(component)
        
        print(f"  ✅ Extracted {len(self.schema_mapping['Components'])} components")

    def _extract_guides(self, df):
        """استخراج بيانات الأدلة"""
        print("  📖 Extracting Guides...")
        
        # البحث عن أعمدة الأدلة
        guide_keywords = ['guide', 'tutorial', 'title', 'instruction']
        guide_cols = [col for col in df.columns if any(kw in col for kw in guide_keywords)]
        
        if guide_cols:
            guides_df = df[guide_cols].drop_duplicates()
        else:
            guides_df = pd.DataFrame({
                'guide_title': ['Getting Started with Arduino UNO']
            })
        
        for idx, row in guides_df.iterrows():
            guide = {
                'GuideID': idx + 1,
                'DeviceID': 1,
                'Title': str(row.iloc[0] if len(row) > 0 else f'Guide_{idx}'),
                'DateCreated': datetime.now().date().isoformat(),
                'GuideURL': None,
                'CreatedAt': datetime.now().isoformat()
            }
            self.schema_mapping['Guides'].append(guide)
        
        print(f"  ✅ Extracted {len(self.schema_mapping['Guides'])} guides")

    def _extract_steps(self, df):
        """استخراج بيانات الخطوات"""
        print("  👣 Extracting Steps...")
        
        # البحث عن أعمدة الخطوات
        step_keywords = ['step', 'instruction', 'description', 'procedure']
        step_cols = [col for col in df.columns if any(kw in col for kw in step_keywords)]
        
        if step_cols:
            steps_df = df[step_cols].drop_duplicates()
        else:
            # إنشاء خطوات افتراضية
            steps_df = pd.DataFrame({
                'step': [
                    'Connect the USB cable to your Arduino UNO',
                    'Install the Arduino IDE on your computer',
                    'Select your board in the Tools menu',
                    'Upload the first sketch'
                ]
            })
        
        for guide_id, guide in enumerate(self.schema_mapping['Guides'], 1):
            for step_num, row in steps_df.iterrows():
                step = {
                    'StepID': len(self.schema_mapping['Steps']) + 1,
                    'GuideID': guide_id,
                    'StepNumber': step_num + 1,
                    'Description': str(row.iloc[0] if len(row) > 0 else f'Step {step_num + 1}'),
                    'CreatedAt': datetime.now().isoformat()
                }
                self.schema_mapping['Steps'].append(step)
        
        print(f"  ✅ Extracted {len(self.schema_mapping['Steps'])} steps")

    def generate_sql_inserts(self):
        """توليد عمليات INSERT للـ SQL"""
        print("\n🗄️  Generating SQL INSERT statements...")
        
        sql_statements = []
        
        # INSERT Devices
        sql_statements.append("-- DEVICES\n")
        for device in self.schema_mapping['Devices']:
            sql = f"""INSERT INTO Devices (DeviceName, DeviceType, ImageURL) 
VALUES ('{device['DeviceName']}', '{device['DeviceType']}', {f"'{device['ImageURL']}'" if device['ImageURL'] else 'NULL'});"""
            sql_statements.append(sql)
        
        # INSERT Components
        sql_statements.append("\n-- COMPONENTS\n")
        for component in self.schema_mapping['Components']:
            sql = f"""INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES ({component['DeviceID']}, '{component['ComponentName']}', '{component['Description'].replace("'", "''")}');"""
            sql_statements.append(sql)
        
        # INSERT Guides
        sql_statements.append("\n-- GUIDES\n")
        for guide in self.schema_mapping['Guides']:
            sql = f"""INSERT INTO Guides (DeviceID, Title, DateCreated) 
VALUES ({guide['DeviceID']}, '{guide['Title']}', '{guide['DateCreated']}');"""
            sql_statements.append(sql)
        
        # INSERT Steps
        sql_statements.append("\n-- STEPS\n")
        for step in self.schema_mapping['Steps']:
            sql = f"""INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES ({step['GuideID']}, {step['StepNumber']}, '{step['Description'].replace("'", "''")}');"""
            sql_statements.append(sql)
        
        return '\n'.join(sql_statements)

    def save_results(self):
        """حفظ النتائج"""
        print("\n💾 Saving results...")
        
        # 1. حفظ البيانات المنظفة
        cleaned_file = self.processed_path / "cleaned_data.json"
        with open(cleaned_file, 'w', encoding='utf-8') as f:
            json.dump(self.schema_mapping, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved cleaned data to: {cleaned_file}")
        
        # 2. حفظ عمليات SQL
        sql_statements = self.generate_sql_inserts()
        sql_file = self.output_path / "database_inserts.sql"
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(sql_statements)
        print(f"✅ Saved SQL inserts to: {sql_file}")
        
        # 3. حفظ ملخص التنظيف
        summary = {
            "timestamp": datetime.now().isoformat(),
            "cleaned_data": {
                "devices": len(self.schema_mapping['Devices']),
                "components": len(self.schema_mapping['Components']),
                "guides": len(self.schema_mapping['Guides']),
                "steps": len(self.schema_mapping['Steps'])
            },
            "sample_data": {
                "devices": self.schema_mapping['Devices'][:2],
                "components": self.schema_mapping['Components'][:2],
                "guides": self.schema_mapping['Guides'][:2],
                "steps": self.schema_mapping['Steps'][:2]
            }
        }
        
        summary_file = self.output_path / "cleaning_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved summary to: {summary_file}")
        
        return cleaned_file, sql_file, summary_file

    def print_report(self):
        """طباعة تقرير ملخص"""
        print("\n" + "=" * 70)
        print("📊 DATA CLEANING REPORT")
        print("=" * 70)
        
        print(f"\n✅ DEVICES ({len(self.schema_mapping['Devices'])})")
        for device in self.schema_mapping['Devices'][:3]:
            print(f"   • {device['DeviceName']} ({device['DeviceType']})")
        
        print(f"\n✅ COMPONENTS ({len(self.schema_mapping['Components'])})")
        for component in self.schema_mapping['Components'][:3]:
            print(f"   • {component['ComponentName']}")
        
        print(f"\n✅ GUIDES ({len(self.schema_mapping['Guides'])})")
        for guide in self.schema_mapping['Guides'][:3]:
            print(f"   • {guide['Title']}")
        
        print(f"\n✅ STEPS ({len(self.schema_mapping['Steps'])})")
        for step in self.schema_mapping['Steps'][:5]:
            print(f"   Step {step['StepNumber']}: {step['Description'][:50]}...")
        
        print("\n" + "=" * 70)

def main():
    print("=" * 70)
    print("🧹 SmartMentor: Automatic Data Cleaning & Schema Mapping")
    print("=" * 70)
    
    cleaner = DataCleaner()
    
    # 1. تحميل البيانات
    cleaner.load_raw_data()
    
    # 2. تنظيف البيانات
    cleaner.clean_data()
    
    # 3. تصنيف في الـ Schema
    cleaner.map_to_schema()
    
    # 4. حفظ النتائج
    cleaner.save_results()
    
    # 5. طباعة التقرير
    cleaner.print_report()
    
    print("\n✅ Data cleaning complete!")

if __name__ == "__main__":
    main()
