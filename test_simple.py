# test_simple.py
import requests
from bs4 import BeautifulSoup
import os

def simple_test():
    print("Testing simple scraper...")
    
    # Create folders
    os.makedirs('data/raw/scraped_json', exist_ok=True)
    
    # Test simple page
    url = "https://docs.arduino.cc/"
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("Website is working")
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            print(f"Page title: {title.text if title else 'No title'}")
        else:
            print(f"Connection error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_test()