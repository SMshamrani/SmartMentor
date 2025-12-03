# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    
    # Database Settings
    DB_NAME = os.getenv("DB_NAME", "arduino_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    # Paths
    DATA_DIR = "data"
    RAW_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
    SCRAPED_IMAGES_DIR = os.path.join(DATA_DIR, "scraped_images")
    
    @classmethod
    def ensure_directories(cls):
        """ينشئ المجلدات الضرورية إذا لم تكن موجودة"""
        dirs = [cls.RAW_DIR, cls.PROCESSED_DIR, cls.SCRAPED_IMAGES_DIR]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)