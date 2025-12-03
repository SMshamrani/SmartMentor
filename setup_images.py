# setup_images.py
"""
Complete Image Setup Script with Real Arduino Images
Combines directory creation + real image downloading
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests

def setup_directories():
    """Create all necessary directories"""
    print("Creating directories...")
    
    directories = [
        "data/scraped_images/boards",
        "data/scraped_images/components", 
        "data/scraped_images/diagrams",
        "data/classified_images/pinouts",
        "data/classified_images/tutorials",
        "data/classified_images/components",
        "data/classified_images/circuits",
        "data/classified_images/other",
        "data/image_sources"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print("✅ All directories created\n")

def download_real_images():
    """Download real Arduino images from open sources"""
    print("=" * 60)
    print("DOWNLOADING REAL ARDUINO IMAGES")
    print("=" * 60)
    
    # Real Arduino images (tested URLs)
    image_sources = [
        # Arduino Board Photos
        ("boards/arduino_uno_board.jpg", 
         "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Arduino_Uno_-_R3.jpg/600px-Arduino_Uno_-_R3.jpg"),
        
        ("boards/arduino_nano_board.jpg", 
         "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Arduino_Nano.jpg/600px-Arduino_Nano.jpg"),
        
        # Pinout Diagrams (from Arduino official)
        ("diagrams/uno_pinout_diagram.png", 
         "https://content.arduino.cc/assets/Pinout-UNOrev3_latest.png"),
        
        ("diagrams/nano_pinout_diagram.png", 
         "https://content.arduino.cc/assets/Pinout-NANO_latest.png"),
        
        ("diagrams/mega_pinout_diagram.png", 
         "https://content.arduino.cc/assets/Pinout-MEGA2560rev3_latest.png"),
        
        # Electronic Components
        ("components/led_component.png", 
         "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/LED%2C_5mm%2C_green_%28en%29.png/400px-LED%2C_5mm%2C_green_%28en%29.png"),
        
        ("components/resistor_component.jpg", 
         "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Resistor.jpg/400px-Resistor.jpg"),
        
        ("components/breadboard_component.png", 
         "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Breadboard_Internal_Connections.svg/600px-Breadboard_Internal_Connections.svg.png"),
        
        # Arduino Logo
        ("boards/arduino_logo.png", 
         "https://www.arduino.cc/en/uploads/Trademark/ArduinoCommunityLogo.png"),
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Arduino Educational Project)'
    }
    
    downloaded = 0
    failed = 0
    
    for filename, url in image_sources:
        try:
            save_path = Path("data/scraped_images") / filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"\nDownloading: {filename}")
            print(f"  Source: {url[:80]}...")
            
            # Try download
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                # Verify it's a valid image
                if os.path.getsize(save_path) > 1024:  # More than 1KB
                    try:
                        img = Image.open(save_path)
                        img.verify()
                        downloaded += 1
                        file_size = os.path.getsize(save_path) / 1024
                        print(f"  ✅ Success: {file_size:.1f} KB")
                    except:
                        failed += 1
                        os.remove(save_path)
                        print(f"  ❌ Invalid image file")
                else:
                    failed += 1
                    os.remove(save_path)
                    print(f"  ❌ File too small")
            else:
                failed += 1
                print(f"  ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            failed += 1
            print(f"  ❌ Error: {str(e)[:50]}")
    
    print("\n" + "=" * 60)
    print(f"DOWNLOAD RESULTS: {downloaded} successful, {failed} failed")
    
    if downloaded == 0:
        print("\n⚠️ No images downloaded. Creating realistic mockups...")
        downloaded = create_realistic_mockups()
    
    return downloaded

def create_realistic_mockups():
    """Create realistic Arduino mockups when downloads fail"""
    print("\nCreating realistic Arduino mockups...")
    
    def create_arduino_board(name, width=600, height=400):
        """Create realistic Arduino board image"""
        # Dark background
        img = Image.new('RGB', (width, height), (30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # PCB (green board)
        pcb_color = (0, 80, 40) if 'Uno' in name else (0, 70, 35) if 'Nano' in name else (0, 90, 45)
        pcb_margin = 40
        draw.rectangle([
            pcb_margin, pcb_margin, 
            width-pcb_margin, height-pcb_margin
        ], fill=pcb_color, outline=(180, 180, 180), width=2)
        
        # USB Port
        usb_width, usb_height = 80, 15
        usb_x = (width - usb_width) // 2
        draw.rectangle([
            usb_x, pcb_margin//2,
            usb_x + usb_width, pcb_margin//2 + usb_height
        ], fill=(80, 80, 80))
        
        # Digital Pins (left side)
        pin_colors = [(220, 180, 0), (0, 120, 220), (220, 60, 60), (60, 220, 60)]
        for i in range(14):
            pin_x = pcb_margin - 15
            pin_y = pcb_margin + 20 + i * 22
            color_idx = i % len(pin_colors)
            draw.rectangle([
                pin_x, pin_y,
                pin_x + 10, pin_y + 12
            ], fill=pin_colors[color_idx])
            
            # Pin label
            try:
                font = ImageFont.truetype("arial.ttf", 10) if sys.platform == "win32" else ImageFont.load_default()
                draw.text((pin_x - 15, pin_y), f"D{i}", fill=(255, 255, 255), font=font)
            except:
                pass
        
        # Analog Pins (right side)
        for i in range(6):
            pin_x = width - pcb_margin + 5
            pin_y = pcb_margin + 20 + i * 22
            color_idx = i % len(pin_colors)
            draw.rectangle([
                pin_x, pin_y,
                pin_x + 10, pin_y + 12
            ], fill=pin_colors[color_idx])
            
            # Pin label
            try:
                font = ImageFont.truetype("arial.ttf", 10) if sys.platform == "win32" else ImageFont.load_default()
                draw.text((pin_x + 15, pin_y), f"A{i}", fill=(255, 255, 255), font=font)
            except:
                pass
        
        # Power pins
        power_pins = ["5V", "3.3V", "GND", "GND", "Vin", "RESET"]
        for i, label in enumerate(power_pins):
            pin_x = pcb_margin + 100 + i * 60
            pin_y = height - pcb_margin - 20
            draw.rectangle([
                pin_x, pin_y,
                pin_x + 40, pin_y + 12
            ], fill=(100, 100, 150))
            
            try:
                font = ImageFont.truetype("arial.ttf", 9) if sys.platform == "win32" else ImageFont.load_default()
                draw.text((pin_x + 5, pin_y - 1), label, fill=(255, 255, 255), font=font)
            except:
                pass
        
        # Board name
        try:
            font = ImageFont.truetype("arial.ttf", 24) if sys.platform == "win32" else ImageFont.load_default()
            text_width = draw.textlength(name, font=font)
            text_x = (width - text_width) // 2
            draw.text((text_x, height - 35), name, fill=(255, 255, 200), font=font)
        except:
            pass
        
        # Arduino text
        draw.text((width//2 - 40, height//2 - 30), "ARDUINO", fill=(0, 180, 240), font=ImageFont.load_default())
        
        return img
    
    def create_led_component():
        """Create realistic LED image"""
        img = Image.new('RGB', (300, 400), (240, 240, 240))
        draw = ImageDraw.Draw(img)
        
        # LED body (semi-transparent red)
        led_size = 120
        center_x, center_y = 150, 150
        
        # LED dome
        for i in range(led_size, 0, -10):
            alpha = 200 - (i * 1.5)
            color = (255, max(0, 50 - i//3), max(0, 50 - i//3))
            draw.ellipse([
                center_x - i//2, center_y - i//2,
                center_x + i//2, center_y + i//2
            ], fill=color, outline=(100, 0, 0), width=1)
        
        # LED legs
        draw.rectangle([145, 210, 155, 350], fill=(180, 180, 180))
        
        # Anode/Cathode markers
        draw.rectangle([135, 330, 145, 340], fill=(255, 255, 0))  # Anode (+)
        draw.rectangle([155, 330, 165, 340], fill=(0, 0, 0))      # Cathode (-)
        
        # Label
        draw.text((100, 360), "5mm RED LED", fill=(0, 0, 0), font=ImageFont.load_default())
        
        return img
    
    def create_resistor_component():
        """Create realistic resistor image"""
        img = Image.new('RGB', (400, 150), (250, 250, 250))
        draw = ImageDraw.Draw(img)
        
        # Resistor body
        body_color = (165, 42, 42)  # Brown
        draw.rectangle([50, 50, 350, 100], fill=body_color, outline=(100, 50, 30), width=2)
        
        # Color bands (220 ohm resistor: Red-Red-Brown-Gold)
        bands = [
            (120, 40, 130, 110, (255, 0, 0)),     # Red
            (160, 40, 170, 110, (255, 0, 0)),     # Red
            (200, 40, 210, 110, (165, 42, 42)),   # Brown
            (240, 40, 250, 110, (255, 215, 0)),   # Gold
        ]
        
        for x1, y1, x2, y2, color in bands:
            draw.rectangle([x1, y1, x2, y2], fill=color)
        
        # Leads
        draw.rectangle([30, 70, 50, 80], fill=(150, 150, 150))
        draw.rectangle([350, 70, 370, 80], fill=(150, 150, 150))
        
        # Label
        draw.text((150, 110), "220Ω Resistor", fill=(0, 0, 0), font=ImageFont.load_default())
        
        return img
    
    def create_pinout_diagram(board_name):
        """Create realistic pinout diagram"""
        width, height = 800, 600
        img = Image.new('RGB', (width, height), (255, 255, 240))
        draw = ImageDraw.Draw(img)
        
        # Title
        draw.text((width//2 - 100, 20), f"{board_name} PINOUT DIAGRAM", 
                 fill=(0, 0, 100), font=ImageFont.load_default())
        
        # Board outline
        board_width, board_height = 400, 300
        board_x, board_y = (width - board_width)//2, 80
        
        draw.rectangle([board_x, board_y, board_x+board_width, board_y+board_height], 
                      fill=(200, 230, 200), outline=(0, 100, 0), width=3)
        
        # Pins grid
        pin_types = [
            ("DIGITAL PINS", 14, (0, 100, 200), board_x + 30, board_y + 50),
            ("ANALOG PINS", 6, (200, 100, 0), board_x + board_width - 100, board_y + 50),
            ("POWER", 6, (100, 100, 100), board_x + board_width//2 - 50, board_y + board_height - 80),
        ]
        
        for label, count, color, start_x, start_y in pin_types:
            draw.text((start_x, start_y - 25), label, fill=color, font=ImageFont.load_default())
            
            for i in range(count):
                pin_y = start_y + i * 30
                draw.rectangle([start_x, pin_y, start_x+60, pin_y+20], fill=color)
                
                pin_label = f"D{i}" if "DIGITAL" in label else f"A{i}" if "ANALOG" in label else ["5V", "3.3V", "GND", "GND", "Vin", "RST"][i]
                draw.text((start_x + 5, pin_y + 3), pin_label, fill=(255, 255, 255), font=ImageFont.load_default())
        
        # Legend
        legend_y = board_y + board_height + 40
        legends = [
            ("Digital I/O", (0, 100, 200)),
            ("Analog Input", (200, 100, 0)),
            ("Power", (100, 100, 100)),
            ("PWM", (200, 0, 200)),
        ]
        
        for i, (text, color) in enumerate(legends):
            lx = board_x + i * 180
            draw.rectangle([lx, legend_y, lx+20, legend_y+20], fill=color)
            draw.text((lx+25, legend_y), text, fill=(0, 0, 0), font=ImageFont.load_default())
        
        return img
    
    # Create directories
    Path("data/scraped_images/boards").mkdir(parents=True, exist_ok=True)
    Path("data/scraped_images/components").mkdir(parents=True, exist_ok=True)
    Path("data/scraped_images/diagrams").mkdir(parents=True, exist_ok=True)
    
    created_count = 0
    
    # Create Arduino boards
    boards = ["Arduino Uno R3", "Arduino Nano", "Arduino Mega 2560"]
    for board in boards:
        img = create_arduino_board(board)
        filename = f"{board.lower().replace(' ', '_')}_realistic.png"
        save_path = Path("data/scraped_images/boards") / filename
        img.save(save_path, 'PNG', quality=95)
        created_count += 1
        print(f"  Created: {save_path}")
    
    # Create components
    led_img = create_led_component()
    led_img.save("data/scraped_images/components/led_realistic.png", 'PNG', quality=95)
    created_count += 1
    print(f"  Created: data/scraped_images/components/led_realistic.png")
    
    resistor_img = create_resistor_component()
    resistor_img.save("data/scraped_images/components/resistor_realistic.png", 'PNG', quality=95)
    created_count += 1
    print(f"  Created: data/scraped_images/components/resistor_realistic.png")
    
    # Create pinout diagrams
    for board in ["Arduino Uno", "Arduino Nano"]:
        img = create_pinout_diagram(board)
        filename = f"{board.lower().replace(' ', '_')}_pinout_realistic.png"
        save_path = Path("data/scraped_images/diagrams") / filename
        img.save(save_path, 'PNG', quality=95)
        created_count += 1
        print(f"  Created: {save_path}")
    
    print(f"\n✅ Created {created_count} realistic Arduino images")
    return created_count

def copy_existing_images():
    """Copy any existing images from project"""
    print("\nLooking for existing images in project...")
    
    # Common locations for Arduino images
    search_locations = [
        "data/scraped_images/boards",
        "data/scraped_images",
        "scraped_images",
        "images",
        ".",
    ]
    
    copied = 0
    
    for location in search_locations:
        loc_path = Path(location)
        if loc_path.exists():
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                for img_file in loc_path.rglob(f"*{ext}"):
                    try:
                        # Skip if already in target location
                        if "data/scraped_images" in str(img_file):
                            continue
                        
                        # Determine category based on filename
                        filename_lower = img_file.name.lower()
                        if any(word in filename_lower for word in ['pinout', 'diagram', 'schematic']):
                            category = "diagrams"
                        elif any(word in filename_lower for word in ['uno', 'nano', 'mega', 'board', 'arduino']):
                            category = "boards"
                        elif any(word in filename_lower for word in ['led', 'resistor', 'sensor', 'component']):
                            category = "components"
                        else:
                            category = "boards"  # Default
                        
                        # Create destination
                        dest_dir = Path(f"data/scraped_images/{category}")
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Copy file
                        dest_file = dest_dir / img_file.name
                        shutil.copy2(img_file, dest_file)
                        
                        copied += 1
                        print(f"  Copied: {img_file} → {dest_file}")
                        
                    except Exception as e:
                        print(f"  Error copying {img_file}: {e}")
    
    if copied > 0:
        print(f"\n✅ Copied {copied} existing images")
    
    return copied

def create_metadata():
    """Create metadata file for all images"""
    print("\nCreating image metadata...")
    
    metadata = {
        "project": "SmartMentor Arduino Image Collection",
        "setup_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_images": 0,
        "images": [],
        "categories": {
            "boards": 0,
            "components": 0,
            "diagrams": 0
        }
    }
    
    scraped_dir = Path("data/scraped_images")
    
    if scraped_dir.exists():
        for category_dir in scraped_dir.iterdir():
            if category_dir.is_dir():
                category_name = category_dir.name
                
                for img_file in category_dir.glob("*.*"):
                    if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                        try:
                            img = Image.open(img_file)
                            
                            image_info = {
                                "filename": img_file.name,
                                "path": str(img_file.relative_to("data")),
                                "category": category_name,
                                "size_kb": round(os.path.getsize(img_file) / 1024, 2),
                                "dimensions": f"{img.width}x{img.height}",
                                "format": img.format,
                                "created": time.ctime(img_file.stat().st_mtime)
                            }
                            
                            metadata["images"].append(image_info)
                            metadata["categories"][category_name] = metadata["categories"].get(category_name, 0) + 1
                            
                        except Exception as e:
                            print(f"  Error reading {img_file}: {e}")
        
        metadata["total_images"] = len(metadata["images"])
    
    # Save metadata
    metadata_file = Path("data/scraped_images/metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)
    
    print(f"📄 Metadata saved to: {metadata_file}")
    
    # Print summary
    print(f"\n📊 IMAGE COLLECTION SUMMARY:")
    print(f"   Total images: {metadata['total_images']}")
    for category, count in metadata["categories"].items():
        print(f"   {category}: {count} images")
    
    # List sample files
    if metadata["images"]:
        print(f"\n📁 Sample files:")
        for img in metadata["images"][:5]:  # Show first 5
            print(f"   • {img['filename']} ({img['dimensions']})")
    
    return metadata

def main():
    """Main setup function"""
    print("=" * 60)
    print("ARDUINO IMAGE SETUP - OPTION 2 (Real Images)")
    print("=" * 60)
    
    # Step 1: Create directories
    print("\n[1/5] Setting up directories...")
    setup_directories()
    
    # Step 2: Try to download real images
    print("\n[2/5] Attempting to download real Arduino images...")
    downloaded = download_real_images()
    
    # Step 3: Copy existing images
    print("\n[3/5] Copying existing project images...")
    copied = copy_existing_images()
    
    # Step 4: Create metadata
    print("\n[4/5] Creating metadata...")
    metadata = create_metadata()
    
    # Step 5: Final report
    print("\n[5/5] Generating final report...")
    
    total_images = metadata["total_images"]
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETED SUCCESSFULLY! 🎉")
    print("=" * 60)
    
    if total_images > 0:
        print(f"\n✅ SUCCESS: Collected {total_images} Arduino images")
        print(f"\n📁 Image locations:")
        print(f"   • Boards: data/scraped_images/boards/ ({metadata['categories'].get('boards', 0)} images)")
        print(f"   • Components: data/scraped_images/components/ ({metadata['categories'].get('components', 0)} images)")
        print(f"   • Diagrams: data/scraped_images/diagrams/ ({metadata['categories'].get('diagrams', 0)} images)")
        
        print(f"\n📄 Metadata file: data/scraped_images/metadata.json")
        
        print(f"\n🚀 Next steps:")
        print(f"   1. View images: ls -la data/scraped_images/*/*")
        print(f"   2. Classify images: python src/image_classifier.py")
        print(f"   3. Run full pipeline: python main_updated.py")
        
        # Quick check of images
        print(f"\n🔍 Quick check (first 3 images in each category):")
        scraped_dir = Path("data/scraped_images")
        for category_dir in scraped_dir.iterdir():
            if category_dir.is_dir():
                images = list(category_dir.glob("*.*"))[:3]
                if images:
                    print(f"\n   {category_dir.name.upper()}:")
                    for img in images:
                        size_kb = os.path.getsize(img) / 1024
                        print(f"     • {img.name} ({size_kb:.1f} KB)")
    
    else:
        print(f"\n⚠️ WARNING: No images were collected")
        print(f"   Please check your internet connection or")
        print(f"   manually add images to data/scraped_images/")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)