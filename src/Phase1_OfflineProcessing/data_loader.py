# src/Phase1_OfflineProcessing/data_loader.py

import pandas as pd
import json
from pathlib import Path

class DataLoader:
    def __init__(self):
        self.raw_path = Path("data/raw/scraped_data")
        self.processed_path = Path("data/processed")
    
    def load_xlsx_csv(self):
        """قراءة الملفات وتحويلها إلى JSON"""
        
        # قراءة XLSX
        df_xlsx = pd.read_excel(
            self.raw_path / "arduino_uno_raw.xlsx"
        )
        
        # قراءة CSV
        df_csv = pd.read_csv(
            self.raw_path / "arduino_uno_raw.csv"
        )
        
        # دمج البيانات
        combined_data = pd.concat([df_xlsx, df_csv], ignore_index=True)
        
        # تنظيف البيانات
        combined_data = combined_data.drop_duplicates()
        
        # تحويل إلى JSON منظم
        structured_data = self.structure_data(combined_data)
        
        # حفظ JSON
        self.save_json(structured_data)
        
        return structured_data
    
    def structure_data(self, df):
        """تحويل DataFrame إلى هيكل منطقي"""
        
        structured = {
            "device": {
                "name": "Arduino UNO R3",
                "description": "Microcontroller board based on ATmega328P",
                "official_link": "https://docs.arduino.cc/tutorials/uno-rev3/getting-started/",
                "specifications": {},
                "components": [],
                "pinout": {},
                "tutorials": []
            }
        }
        
        # استخراج البيانات من DataFrame
        for col in df.columns:
            if "pin" in col.lower():
                structured["device"]["pinout"][col] = df[col].tolist()
            elif "component" in col.lower():
                structured["device"]["components"].append(df[col].tolist())
            elif "spec" in col.lower():
                structured["device"]["specifications"][col] = df[col].tolist()
            elif "tutorial" in col.lower():
                structured["device"]["tutorials"].append(df[col].tolist())
        
        return structured
    
    def save_json(self, data):
        """حفظ البيانات في JSON"""
        output_file = self.processed_path / "arduino_uno_structured.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved to: {output_file}")

# استخدام:
loader = DataLoader()
data = loader.load_xlsx_csv()
print(data)
