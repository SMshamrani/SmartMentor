# config.py
"""
Configuration settings for the Arduino Data Scraper
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Scraper Configuration
SCRAPER_CONFIG = {
    'base_url': 'https://docs.arduino.cc',
    'request_delay': 2,  # seconds between requests
    'timeout': 30,  # request timeout in seconds
    'max_retries': 3,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'arduino_guide'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# File Paths
DATA_PATHS = {
    'raw_json': 'data/raw/scraped_json',
    'raw_images': 'data/raw/scraped_images',
    'cleaned_data': 'data/processed/cleaned_data',
    'classified_images': 'data/processed/classified_images'
}

# Application Settings
APP_CONFIG = {
    'log_level': 'INFO',
    'max_images_per_device': 5,
    'max_steps_per_guide': 15
}