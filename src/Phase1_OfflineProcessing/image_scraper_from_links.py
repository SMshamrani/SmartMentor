#!/usr/bin/env python3
"""
Extract images and documentation files from Arduino project pages and official docs.
"""

import json
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class ArduinoProjectImageScraper:
    """Scrape example project images and download official Arduino documentation PDFs."""

    def __init__(self):
        # Example Arduino Project Hub links to scrape images from
        self.project_links = [
            {
                "name": "andon_system",
                "url": "https://projecthub.arduino.cc/ibrahim_magdy/basic-andon-system-using-arduino-uno-r3-and-python-5214b0",
                "description": "Andon System using Arduino UNO",
            },
            {
                "name": "rfid_reader",
                "url": "https://projecthub.arduino.cc/ZJH/buono-uno-r3-with-rc522-rfid-reader-kit-for-makers-ee12fb",
                "description": "UNO R3 with RFID Reader",
            },
            {
                "name": "blinking_led",
                "url": "https://projecthub.arduino.cc/arohansenroy/blinking-led-77a79f",
                "description": "Blinking LED Tutorial",
            },
        ]

        # Official Arduino documentation PDFs (pinout, datasheet, schematics)
        self.document_links = [
            {
                "name": "pinout_diagram",
                "url": "https://docs.arduino.cc/resources/pinouts/A000066-full-pinout.pdf",
                "type": "PDF",
            },
            {
                "name": "datasheet",
                "url": "https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf",
                "type": "PDF",
            },
            {
                "name": "schematics",
                "url": "https://docs.arduino.cc/resources/schematics/A000066-schematics.pdf",
                "type": "PDF",
            },
        ]

        # Directory where images and PDFs will be saved
        self.image_dir = Path("data/raw/scraped_images/project_examples")
        self.image_dir.mkdir(parents=True, exist_ok=True)

        # Dictionary to store scraping results and metadata
        self.results = {
            "timestamp": str(time.time()),
            "images_downloaded": [],
            "pdfs_downloaded": [],
            "failed_downloads": [],
            "project_info": [],
        }

    def scrape_project_images(self):
        """Scrape image URLs from Arduino Project Hub pages and download a subset of them."""
        print("\nScraping Arduino Project Hub for images...")

        for project in self.project_links:
            print(f"\n  Project: {project['name']}")
            print(f"  URL: {project['url']}")

            try:
                response = requests.get(project["url"], timeout=10)
                soup = BeautifulSoup(response.content, "html.parser")

                # Find all image tags in the page
                images = soup.find_all("img")
                print(f"  Found {len(images)} images")

                project_images = []

                # Limit to first 10 images to avoid downloading too many
                for idx, img in enumerate(images[:10]):
                    img_url = img.get("src")
                    img_alt = img.get("alt", f"{project['name']}_image_{idx}")

                    if img_url:
                        # Convert relative URL to absolute URL if needed
                        if not img_url.startswith("http"):
                            img_url = urljoin(project["url"], img_url)

                        # Download the image file
                        success = self.download_image(img_url, img_alt, project["name"])
                        if success:
                            project_images.append(
                                {
                                    "name": img_alt,
                                    "url": img_url,
                                    "project": project["name"],
                                }
                            )

                        # Be polite: short delay between requests
                        time.sleep(0.3)

                # Store summary information for this project
                self.results["project_info"].append(
                    {
                        "project": project["name"],
                        "title": project["description"],
                        "url": project["url"],
                        "images_found": len(project_images),
                    }
                )

            except Exception as e:
                print(f"  Error while scraping project: {e}")
                self.results["failed_downloads"].append(
                    {
                        "project": project["name"],
                        "error": str(e),
                    }
                )

    def download_pdfs(self):
        """Download official Arduino documentation PDFs (pinout, datasheet, schematics)."""
        print("\nDownloading Arduino documentation PDFs...")

        for doc in self.document_links:
            print(f"\n  Downloading: {doc['name']}")

            try:
                response = requests.get(doc["url"], timeout=10)

                if response.status_code == 200:
                    filename = self.image_dir / f"{doc['name']}.pdf"
                    with open(filename, "wb") as f:
                        f.write(response.content)

                    print(f"  Saved: {filename}")
                    self.results["pdfs_downloaded"].append(
                        {
                            "name": doc["name"],
                            "file": str(filename),
                            "size": len(response.content),
                        }
                    )
                else:
                    print(f"  Failed (status {response.status_code})")
                    self.results["failed_downloads"].append(
                        {
                            "doc": doc["name"],
                            "status": response.status_code,
                        }
                    )

                # Short delay between downloads
                time.sleep(0.5)

            except Exception as e:
                print(f"  Error while downloading PDF: {e}")
                self.results["failed_downloads"].append(
                    {
                        "doc": doc["name"],
                        "error": str(e),
                    }
                )

    def download_image(self, url, filename, project_name):
        """Download a single image from the given URL and save it to disk."""
        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                # Detect file extension from URL, fallback to jpg if unknown
                ext = url.split(".")[-1].split("?")[0].lower()
                if ext not in ["jpg", "jpeg", "png", "gif", "svg", "webp"]:
                    ext = "jpg"

                # Clean filename to avoid invalid characters
                clean_name = "".join(c for c in filename if c.isalnum() or c in "-_")
                filepath = self.image_dir / f"{project_name}_{clean_name}.{ext}"

                with open(filepath, "wb") as f:
                    f.write(response.content)

                print(f"    Saved image: {clean_name}")
                self.results["images_downloaded"].append(
                    {
                        "name": clean_name,
                        "project": project_name,
                        "file": str(filepath),
                        "size": len(response.content),
                    }
                )

                return True

            # Non-200 status code considered a failure
            return False

        except Exception as e:
            print(f"    Error downloading {filename}: {e}")
            return False

    def generate_report(self):
        """Print a simple console report summarizing image and PDF downloads."""
        print("\n" + "=" * 70)
        print("IMAGE SCRAPING REPORT")
        print("=" * 70)

        # Images summary
        print(f"\nIMAGES DOWNLOADED: {len(self.results['images_downloaded'])}")
        for img in self.results["images_downloaded"][:5]:
            print(f"   • {img['project']}: {img['name']}")
        if len(self.results["images_downloaded"]) > 5:
            print(f"   ... and {len(self.results['images_downloaded']) - 5} more")

        # PDFs summary
        print(f"\nPDFS DOWNLOADED: {len(self.results['pdfs_downloaded'])}")
        for pdf in self.results["pdfs_downloaded"]:
            size_kb = pdf["size"] / 1024
            print(f"   • {pdf['name']} ({size_kb:.1f} KB)")

        # Failed downloads summary
        print(f"\nFAILED DOWNLOADS: {len(self.results['failed_downloads'])}")
        for fail in self.results["failed_downloads"][:3]:
            print(f"   • {fail}")

        # Project-level summary
        print(f"\nPROJECTS SCRAPED: {len(self.results['project_info'])}")
        for proj in self.results["project_info"]:
            print(f"   • {proj['project']}: {proj['images_found']} images")

        print("\n" + "=" * 70)

    def save_results(self):
        """Save scraping results and metadata to a JSON report file."""
        output_file = Path("data/outputs/image_scraping_report.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\nReport saved to: {output_file}")


def main():
    """Entry point to run the Arduino project image and PDF scraping pipeline."""
    print("=" * 70)
    print("Arduino Project Image Scraper")
    print("=" * 70)

    scraper = ArduinoProjectImageScraper()

    # 1. Scrape and download example project images
    scraper.scrape_project_images()

    # 2. Download official Arduino documentation PDFs
    scraper.download_pdfs()

    # 3. Print a console summary report
    scraper.generate_report()

    # 4. Save detailed JSON report to disk
    scraper.save_results()

    print("\nImage scraping pipeline completed.")


if __name__ == "__main__":
    main()
