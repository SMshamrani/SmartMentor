# src/image_classifier.py
"""
Image Classifier Module for Arduino Project
Classifies Arduino-related images using machine learning or rule-based methods
"""

import os
import json
import shutil
from pathlib import Path
from PIL import Image
import numpy as np
from collections import Counter

class ImageClassifier:
    def __init__(self, use_ml=False):
        self.base_dir = Path("data")
        self.use_ml = use_ml
        
        # Classification categories for Arduino images
        self.categories = {
            "pinouts": ["pinout", "diagram", "pin", "layout", "schematic"],
            "tutorials": ["tutorial", "step", "guide", "instruction", "howto"],
            "components": ["component", "part", "sensor", "module", "board"],
            "circuits": ["circuit", "wiring", "connection", "breadboard"],
            "other": []  # Default category
        }
        
        # File extensions to process
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    
    def extract_features(self, image_path):
        """Extract basic features from image"""
        try:
            with Image.open(image_path) as img:
                features = {
                    "width": img.width,
                    "height": img.height,
                    "aspect_ratio": img.width / img.height if img.height > 0 else 0,
                    "mode": img.mode,
                    "format": img.format,
                    "size_kb": os.path.getsize(image_path) / 1024
                }
                
                # Additional analysis for pinout diagrams
                if img.width > img.height and img.width > 800:
                    features["is_wide"] = True
                    features["likely_pinout"] = True
                else:
                    features["is_wide"] = False
                    features["likely_pinout"] = False
                
                return features
                
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None
    
    def classify_by_filename(self, filename):
        """Classify image based on filename patterns"""
        filename_lower = filename.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    return category
        
        return "other"
    
    def classify_by_features(self, features):
        """Classify image based on extracted features"""
        if not features:
            return "other"
        
        # Rule-based classification
        if features.get("likely_pinout", False):
            return "pinouts"
        
        # Component images often have specific aspect ratios
        if 0.8 < features["aspect_ratio"] < 1.2:
            # Square-ish images might be components
            if features["size_kb"] < 500:  # Smaller files might be icons
                return "components"
        
        # Wide images might be diagrams or tutorials
        if features["width"] > features["height"] * 1.5:
            return "tutorials"
        
        return "other"
    
    def classify_image(self, image_path):
        """Classify a single image using multiple methods"""
        filename = Path(image_path).name
        
        # Method 1: Filename pattern
        category_by_name = self.classify_by_filename(filename)
        
        # Method 2: Image features
        features = self.extract_features(image_path)
        category_by_features = self.classify_by_features(features)
        
        # Combine classifications (prefer filename if clear match)
        if category_by_name != "other":
            final_category = category_by_name
            confidence = 0.8
        else:
            final_category = category_by_features
            confidence = 0.6
        
        return {
            "filename": filename,
            "path": str(image_path),
            "category": final_category,
            "confidence": confidence,
            "features": features,
            "classification_method": "filename" if category_by_name != "other" else "features"
        }
    
    def organize_images(self):
        """Organize images into categorized directories"""
        print("Organizing images into categories...")
        
        source_dir = self.base_dir / "scraped_images"
        dest_base = self.base_dir / "classified_images"
        
        if not source_dir.exists():
            print(f"Source directory not found: {source_dir}")
            return []
        
        # Create destination directories
        for category in self.categories.keys():
            (dest_base / category).mkdir(exist_ok=True, parents=True)
        
        # Find all images
        image_files = []
        for ext in self.image_extensions:
            image_files.extend(source_dir.rglob(f"*{ext}"))
        
        print(f"Found {len(image_files)} images to classify")
        
        classification_results = []
        
        for img_path in image_files:
            try:
                # Classify image
                result = self.classify_image(img_path)
                
                # Determine destination path
                dest_dir = dest_base / result["category"]
                dest_path = dest_dir / img_path.name
                
                # Handle duplicate filenames
                counter = 1
                while dest_path.exists():
                    stem = img_path.stem
                    suffix = img_path.suffix
                    new_name = f"{stem}_{counter}{suffix}"
                    dest_path = dest_dir / new_name
                    counter += 1
                
                # Copy image to categorized directory
                shutil.copy2(img_path, dest_path)
                
                # Update result with new path
                result["new_path"] = str(dest_path.relative_to(self.base_dir))
                result["organized"] = True
                
                classification_results.append(result)
                
                print(f"  Classified: {img_path.name} -> {result['category']} "
                      f"(confidence: {result['confidence']:.2f})")
                
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                classification_results.append({
                    "filename": img_path.name,
                    "path": str(img_path),
                    "error": str(e),
                    "organized": False
                })
        
        return classification_results
    
    def save_classification_report(self, results):
        """Save classification results to report"""
        report_dir = self.base_dir / "image_sources"
        report_dir.mkdir(exist_ok=True)
        
        # Calculate statistics
        total = len(results)
        successful = len([r for r in results if r.get("organized", False)])
        errors = total - successful
        
        category_counts = Counter()
        for result in results:
            if "category" in result:
                category_counts[result["category"]] += 1
        
        report = {
            "classification_date": str(Path(__file__).parent.parent / "timestamp.txt"),
            "total_images": total,
            "successfully_classified": successful,
            "errors": errors,
            "category_distribution": dict(category_counts),
            "images": results,
            "settings": {
                "use_ml": self.use_ml,
                "categories": list(self.categories.keys())
            }
        }
        
        report_file = report_dir / "classification_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=4)
        
        print(f"\nClassification report saved to: {report_file}")
        return report
    
    def generate_summary(self, report):
        """Generate and print summary of classification"""
        print("\n" + "=" * 60)
        print("IMAGE CLASSIFICATION SUMMARY")
        print("=" * 60)
        
        print(f"Total images processed: {report['total_images']}")
        print(f"Successfully classified: {report['successfully_classified']}")
        print(f"Errors: {report['errors']}")
        
        print("\nCategory Distribution:")
        for category, count in report['category_distribution'].items():
            percentage = (count / report['successfully_classified']) * 100
            print(f"  {category}: {count} images ({percentage:.1f}%)")
        
        print("\nSample Classifications:")
        for i, img in enumerate(report['images'][:5]):  # Show first 5
            if img.get("organized", False):
                print(f"  {i+1}. {img['filename']} -> {img['category']} "
                      f"({img.get('confidence', 0):.2f})")
        
        print("=" * 60)

def main():
    """Main function to run image classification"""
    print("Starting image classification...")
    
    # Initialize classifier (set use_ml=True if you have ML model)
    classifier = ImageClassifier(use_ml=False)
    
    # Step 1: Organize images into categories
    print("\n[STEP 1] Organizing images...")
    results = classifier.organize_images()
    
    # Step 2: Save classification report
    print("\n[STEP 2] Saving classification report...")
    report = classifier.save_classification_report(results)
    
    # Step 3: Generate summary
    print("\n[STEP 3] Generating summary...")
    classifier.generate_summary(report)
    
    print("\n✅ Image classification completed!")
    
    # Show directory structure
    print("\nOrganized image structure:")
    classified_dir = Path("data/classified_images")
    if classified_dir.exists():
        for category_dir in classified_dir.iterdir():
            if category_dir.is_dir():
                image_count = len(list(category_dir.glob("*.*")))
                print(f"  {category_dir.name}/: {image_count} images")

if __name__ == "__main__":
    main()