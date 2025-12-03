# src/database_handler.py
import os
import json
import psycopg2
from psycopg2.extras import execute_batch
from config import Config

class DatabaseHandler:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect(self, dbname="arduino_db", user="postgres", password="password", host="localhost", port="5432"):
        """يتصل بقاعدة البيانات"""
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.cursor = self.conn.cursor()
            print("✅ Connected to database successfully")
            return True
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def create_tables(self):
        """ينشئ الجداول من ملف schema.sql"""
        try:
            schema_path = os.path.join("database", "schema.sql")
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            
            self.cursor.execute(schema_sql)
            self.conn.commit()
            print("✅ Tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            self.conn.rollback()
            return False
    
    def insert_scraped_data(self, json_file_path):
        """يدخل بيانات السكريبر إلى قاعدة البيانات"""
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # إدخال البيانات في جدول Devices أولاً
            devices_added = set()
            
            for item in data:
                device_name = item.get("component", "Unknown")
                
                # تحقق إذا كان الجهاز موجوداً بالفعل
                self.cursor.execute(
                    "SELECT DeviceID FROM Devices WHERE DeviceName = %s",
                    (device_name,)
                )
                existing = self.cursor.fetchone()
                
                if not existing and device_name not in devices_added:
                    # أدخل الجهاز الجديد
                    self.cursor.execute(
                        """
                        INSERT INTO Devices (DeviceName, DeviceType, ImageURL) 
                        VALUES (%s, %s, %s)
                        RETURNING DeviceID
                        """,
                        (device_name, item.get("type", "board"), item.get("image", ""))
                    )
                    device_id = self.cursor.fetchone()[0]
                    devices_added.add(device_name)
                    print(f"  Added device: {device_name}")
                elif existing:
                    device_id = existing[0]
                
                # أدخل في جدول Components إذا كان مكوناً
                if item.get("type") == "component":
                    self.cursor.execute(
                        """
                        INSERT INTO Components (DeviceID, ComponentName, Description)
                        VALUES (%s, %s, %s)
                        """,
                        (device_id, device_name, item.get("description", ""))
                    )
                
                # أدخل في جدول Guides
                self.cursor.execute(
                    """
                    INSERT INTO Guides (DeviceID, Title, DateCreated, GuideURL)
                    VALUES (%s, %s, CURRENT_DATE, %s)
                    """,
                    (device_id, f"Guide for {device_name}", item.get("link", ""))
                )
            
            self.conn.commit()
            print(f"✅ Inserted {len(data)} items into database")
            return True
            
        except Exception as e:
            print(f"❌ Error inserting data: {e}")
            self.conn.rollback()
            return False
    
    def insert_llm_classified_data(self, json_file_path):
        """يدخل البيانات المصنفة بواسطة LLM إلى قاعدة البيانات"""
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for item in data:
                original = item.get("original", {})
                category = item.get("category", "Unknown")
                title = original.get("title", "Untitled")
                snippet = original.get("snippet", "")
                
                # أدخل كدليل جديد
                self.cursor.execute(
                    """
                    INSERT INTO Guides (Title, Description, DateCreated, GuideURL)
                    VALUES (%s, %s, CURRENT_DATE, %s)
                    """,
                    (title, f"{snippet} [Category: {category}]", original.get("link", ""))
                )
            
            self.conn.commit()
            print(f"✅ Inserted {len(data)} LLM classified items")
            return True
            
        except Exception as e:
            print(f"❌ Error inserting LLM data: {e}")
            self.conn.rollback()
            return False
    
    def compare_data_counts(self):
        """يقارن عدد البيانات من مصادر مختلفة"""
        try:
            queries = {
                "scraper_devices": "SELECT COUNT(*) FROM Devices",
                "scraper_guides": "SELECT COUNT(*) FROM Guides WHERE DeviceID IS NOT NULL",
                "llm_guides": "SELECT COUNT(*) FROM Guides WHERE DeviceID IS NULL",
                "total_components": "SELECT COUNT(*) FROM Components"
            }
            
            results = {}
            for name, query in queries.items():
                self.cursor.execute(query)
                count = self.cursor.fetchone()[0]
                results[name] = count
            
            print("\n📊 Database Statistics:")
            print("-" * 30)
            for name, count in results.items():
                print(f"{name.replace('_', ' ').title()}: {count}")
            print("-" * 30)
            
            return results
            
        except Exception as e:
            print(f"❌ Error counting data: {e}")
            return {}
    
    def close(self):
        """يغلق الاتصال بقاعدة البيانات"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✅ Database connection closed")

# دالة مساعدة لاختبار الاتصال
def test_database_connection():
    """تختبر الاتصال بقاعدة البيانات"""
    db = DatabaseHandler()
    
    # يمكنك تغيير هذه الإعدادات حسب بيئتك
    if db.connect(dbname="arduino_db", user="postgres", password="password"):
        
        # 1. أنشئ الجداول (فقط إذا لم تكن موجودة)
        db.create_tables()
        
        # 2. أدخل بيانات السكريبر
        scraper_file = "data/scraped_json/comprehensive_arduino_data.json"
        if os.path.exists(scraper_file):
            db.insert_scraped_data(scraper_file)
        else:
            print(f"⚠️ Scraper file not found: {scraper_file}")
        
        # 3. أدخل بيانات LLM المصنفة
        llm_file = "data/processed/llm_classified.json"
        if os.path.exists(llm_file):
            db.insert_llm_classified_data(llm_file)
        else:
            print(f"⚠️ LLM file not found: {llm_file}")
        
        # 4. قارن الإحصائيات
        db.compare_data_counts()
        
        db.close()

if __name__ == "__main__":
    test_database_connection()