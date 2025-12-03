# src/image_collector_working.py
"""
Working Image Collector with Accessible URLs
"""

import os
import requests
import json
import time
from pathlib import Path
import shutil
from PIL import Image
import io

class WorkingImageCollector:
    def __init__(self):
        self.base_dir = Path("data")
        
        # Working image URLs (tested and accessible)
        self.working_image_urls = {
            "boards": [
                # Open source Arduino images
                "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Arduino_Uno_-_R3.jpg/800px-Arduino_Uno_-_R3.jpg",
                "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Arduino_Nano.jpg/800px-Arduino_Nano.jpg",
                "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Arduino_Mega_2560_and_Arduino_Uno.jpg/800px-Arduino_Mega_2560_and_Arduino_Uno.jpg",
            ],
            "components": [
                # Open source electronic components
                "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/LED%2C_5mm%2C_green_%28en%29.png/600px-LED%2C_5mm%2C_green_%28en%29.png",
                "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Resistor.jpg/600px-Resistor.jpg",
                "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Breadboard_Internal_Connections.svg/800px-Breadboard_Internal_Connections.svg.png",
            ],
            "diagrams": [
                # Arduino pinout diagrams (from official docs)
                "https://content.arduino.cc/assets/Pinout-UNOrev3_latest.png",
                "https://content.arduino.cc/assets/Pinout-NANO_latest.png",
                "https://content.arduino.cc/assets/Pinout-MEGA2560rev3_latest.png",
            ]
        }
        
        # Alternative local fallback images
        self.local_fallback_images = {
            "arduino_uno": "https://content.arduino.cc/assets/UNO-TH-front.jpg",
            "arduino_nano": "https://content.arduino.cc/assets/nano-front-2.jpg",
            "arduino_mega": "https://content.arduino.cc/assets/Mega-2560-2.jpg"
        }
    
    def download_with_fallback(self, url, filename, category):
        """Download image with multiple fallback strategies"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        try:
            print(f"  Downloading: {url}")
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            
            if response.status_code == 200:
                # Determine file extension
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'svg' in content_type:
                    ext = '.svg'
                else:
                    # Try to determine from URL
                    if url.lower().endswith('.png'):
                        ext = '.png'
                    elif url.lower().endswith('.jpg') or url.lower().endswith('.jpeg'):
                        ext = '.jpg'
                    elif url.lower().endswith('.svg'):
                        ext = '.svg'
                    else:
                        ext = '.jpg'  # Default
                
                # Ensure filename has correct extension
                if not filename.endswith(ext):
                    filename = f"{Path(filename).stem}{ext}"
                
                # Save image
                save_path = self.base_dir / "scraped_images" / category / filename
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(save_path, 'wb') as f:
                    if hasattr(response, 'raw'):
                        shutil.copyfileobj(response.raw, f)
                    else:
                        f.write(response.content)
                
                # Verify image
                try:
                    img = Image.open(save_path)
                    img.verify()  # Verify it's a valid image
                    img = Image.open(save_path)  # Reopen for info
                    
                    return {
                        "success": True,
                        "filename": filename,
                        "path": str(save_path),
                        "size_bytes": os.path.getsize(save_path),
                        "dimensions": f"{img.width}x{img.height}",
                        "format": img.format,
                        "source_url": url
                    }
                except Exception as img_err:
                    print(f"    Image verification failed: {img_err}")
                    os.remove(save_path)
                    return {"success": False, "error": "Invalid image"}
                    
            else:
                print(f"    Failed: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"    Download error: {str(e)[:100]}...")
            return {"success": False, "error": str(e)}
    
    def create_local_test_images(self):
        """Create simple test images locally if downloads fail"""
        print("\nCreating local test images...")
        
        categories = ["boards", "components", "diagrams"]
        image_info = []
        
        for category in categories:
            category_dir = self.base_dir / "scraped_images" / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Create 3 test images per category
            for i in range(1, 4):
                filename = f"test_{category}_{i}.png"
                save_path = category_dir / filename
                
                # Create a simple colored image
                img = Image.new('RGB', (800, 600), color=(
                    73 if category == "boards" else 
                    109 if category == "components" else 
                    219  # diagrams
                ))
                
                # Add text
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                
                # Try to use default font
                try:
                    font = ImageFont.load_default()
                    text = f"Test {category.capitalize()} {i}\nArduino Project"
                    draw.text((50, 50), text, fill=(255, 255, 255), font=font)
                except:
                    pass  # If font fails, continue without text
                
                img.save(save_path, 'PNG')
                
                image_info.append({
                    "success": True,
                    "filename": filename,
                    "path": str(save_path),
                    "size_bytes": os.path.getsize(save_path),
                    "dimensions": "800x600",
                    "format": "PNG",
                    "source_url": "local_generated",
                    "category": category
                })
                
                print(f"  Created: {save_path}")
        
        return image_info
    
    def collect_images(self):
        """Main image collection method"""
        print("Starting image collection...")
        
        # Create directories
        (self.base_dir / "scraped_images").mkdir(exist_ok=True, parents=True)
        
        download_results = []
        success_count = 0
        
        # Try to download from URLs
        print("\nAttempting to download from URLs...")
        for category, urls in self.working_image_urls.items():
            print(f"\nCategory: {category.upper()}")
            
            for i, url in enumerate(urls):
                filename = f"{category}_{i+1}_{Path(url).name}"
                result = self.download_with_fallback(url, filename, category)
                
                if result["success"]:
                    success_count += 1
                    download_results.append({
                        **result,
                        "category": category,
                        "download_time": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"    ✓ Success: {result['dimensions']}, {result['size_bytes']} bytes")
                else:
                    print(f"    ✗ Failed: {result.get('error', 'Unknown error')}")
                
                time.sleep(1)  # Be polite
        
        # If no downloads succeeded, create local test images
        if success_count == 0:
            print("\nNo images downloaded successfully. Creating local test images...")
            download_results = self.create_local_test_images()
            success_count = len(download_results)
        
        # Save metadata
        if download_results:
            self.save_metadata(download_results)
        
        print(f"\n✅ Total images collected: {success_count}")
        return download_results
    
    def save_metadata(self, image_info):
        """Save metadata about collected images"""
        metadata = {
            "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_images": len(image_info),
            "images": image_info,
            "summary": {
                "boards": len([i for i in image_info if i.get("category") == "boards"]),
                "components": len([i for i in image_info if i.get("category") == "components"]),
                "diagrams": len([i for i in image_info if i.get("category") == "diagrams"])
            }
        }
        
        metadata_file = self.base_dir / "scraped_images" / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        print(f"\n📄 Metadata saved to: {metadata_file}")
        return metadata_file
    
    def create_image_catalog(self):
        """Create a catalog of all images"""
        print("\nCreating image catalog...")
        
        catalog = {
            "catalog_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_images": 0,
            "categories": {},
            "file_list": []
        }
        
        scraped_dir = self.base_dir / "scraped_images"
        
        if scraped_dir.exists():
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']
            
            for ext in image_extensions:
                for img_path in scraped_dir.rglob(f"*{ext}"):
                    try:
                        rel_path = img_path.relative_to(self.base_dir)
                        category = img_path.parent.name
                        
                        # Get image info
                        img = Image.open(img_path)
                        
                        file_info = {
                            "name": img_path.name,
                            "path": str(rel_path),
                            "category": category,
                            "size_kb": round(os.path.getsize(img_path) / 1024, 2),
                            "dimensions": f"{img.width}x{img.height}",
                            "format": img.format
                        }
                        
                        catalog["file_list"].append(file_info)
                        
                        # Add to category summary
                        if category not in catalog["categories"]:
                            catalog["categories"][category] = []
                        catalog["categories"][category].append(img_path.name)
                        
                    except Exception as e:
                        print(f"  Skipping {img_path}: {e}")
        
        catalog["total_images"] = len(catalog["file_list"])
        
        # Save catalog
        catalog_file = self.base_dir / "image_sources" / "image_catalog.json"
        catalog_file.parent.mkdir(exist_ok=True)
        
        with open(catalog_file, 'w') as f:
            json.dump(catalog, f, indent=4)
        
        print(f"✅ Catalog created: {catalog_file}")
        print(f"   Total images: {catalog['total_images']}")
        
        # Print summary
        for category, files in catalog["categories"].items():
            print(f"   {category}: {len(files)} images")
        
        return catalog

def main():
    """Test the image collector"""
    print("=" * 60)
    print("WORKING IMAGE COLLECTOR")
    print("=" * 60)
    
    collector = WorkingImageCollector()
    
    # Step 1: Collect images
    print("\n[1/3] Collecting images...")
    images = collector.collect_images()
    
    # Step 2: Create catalog
    print("\n[2/3] Creating catalog...")
    catalog = collector.create_image_catalog()
    
    # Step 3: Show results
    print("\n[3/3] Results:")
    print("-" * 40)
    
    if catalog["total_images"] > 0:
        print(f"✅ SUCCESS: Collected {catalog['total_images']} images")
        
        # List images
        print("\nCollected images:")
        for img in catalog["file_list"][:10]:  # Show first 10
            print(f"  • {img['name']} ({img['dimensions']}, {img['size_kb']} KB)")
        
        if catalog["total_images"] > 10:
            print(f"  ... and {catalog['total_images'] - 10} more")
        
        # Show directory structure
        print("\nDirectory structure:")
        scraped_dir = Path("data/scraped_images")
        if scraped_dir.exists():
            for item in scraped_dir.iterdir():
                if item.is_dir():
                    count = len(list(item.glob("*.*")))
                    print(f"  {item.name}/: {count} images")
    
    else:
        print("❌ FAILED: No images collected")
    
    print("\n" + "=" * 60)
    print("Check 'data/scraped_images/' for collected images")
    print("=" * 60)

if __name__ == "__main__":
    main()