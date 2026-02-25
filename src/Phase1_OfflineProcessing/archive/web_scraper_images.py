# src/Phase1_OfflineProcessing/web_scraper_images.py

import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class ArduinoDocsScraper:
    """Scrape official Arduino docs for images related to the UNO getting started page."""

    def __init__(self):
        # Base site URL for Arduino docs
        self.base_url = "https://docs.arduino.cc"
        # Specific tutorial page for Arduino UNO getting started
        self.tutorial_url = "https://docs.arduino.cc/tutorials/uno-rev3/getting-started/"
        # Directory where downloaded images will be stored
        self.image_dir = Path("data/raw/scraped_images/official_docs")
        self.image_dir.mkdir(parents=True, exist_ok=True)

    def scrape_getting_started_images(self):
        """Fetch the getting started page and download all images found on it."""
        try:
            # Request the tutorial page HTML
            response = requests.get(self.tutorial_url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all image tags on the page
            images = soup.find_all("img")
            print(f"Found {len(images)} images on the page")

            for idx, img in enumerate(images):
                try:
                    img_url = img.get("src")
                    img_alt = img.get("alt", f"image_{idx}")

                    if img_url:
                        # Build absolute URL if the src is relative
                        if img_url.startswith("http"):
                            full_url = img_url
                        else:
                            full_url = urljoin(self.base_url, img_url)

                        # Download the image file
                        self.download_image(full_url, img_alt)

                        # Small delay between downloads to avoid overloading the server
                        time.sleep(0.5)

                except Exception as e:
                    print(f"Warning: Error processing image {idx}: {e}")

        except Exception as e:
            print(f"Failed to scrape Arduino docs: {e}")

    def download_image(self, url, filename):
        """Download a single image from a given URL and save it to disk."""
        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                # Try to detect file extension from the URL
                ext = url.split(".")[-1].split("?")[0].lower()
                if ext not in ["jpg", "jpeg", "png", "gif", "svg"]:
                    ext = "jpg"

                # Clean the filename to remove invalid characters
                clean_filename = "".join(
                    c for c in filename if c.isalnum() or c in "-_"
                )

                filepath = self.image_dir / f"{clean_filename}.{ext}"
                with open(filepath, "wb") as f:
                    f.write(response.content)

                print(f"Saved image to: {filepath}")

        except Exception as e:
            print(f"Download failed for {filename}: {e}")


# Example usage (can be kept for manual testing)
if __name__ == "__main__":
    scraper = ArduinoDocsScraper()
    scraper.scrape_getting_started_images()
