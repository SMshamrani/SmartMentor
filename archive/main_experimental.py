# main_updated.py
"""
Updated Main Pipeline for SmartMentor Arduino Project
Includes image collection and classification
"""

import os
import sys
import json
import datetime
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config import Config

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        "data/raw",
        "data/processed",
        "data/scraped_json",
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
    
    print("✅ All directories created")

def run_image_collection():
    """Run image collection pipeline"""
    print("\n" + "=" * 60)
    print("IMAGE COLLECTION PIPELINE")
    print("=" * 60)
    
    try:
        from image_collector import ImageCollector
        
        collector = ImageCollector()
        
        # Step 1: Download sample images
        print("\n[1/3] Downloading Arduino images...")
        downloaded = collector.download_sample_images()
        
        # Step 2: Create catalog
        print("\n[2/3] Creating image catalog...")
        catalog = collector.create_image_catalog()
        
        # Step 3: Generate report
        print("\n[3/3] Generating image report...")
        report = collector.generate_image_report()
        
        print(f"\n✅ Image collection completed: {report['summary']['total_images']} images")
        return True
        
    except Exception as e:
        print(f"❌ Image collection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_image_classification():
    """Run image classification pipeline"""
    print("\n" + "=" * 60)
    print("IMAGE CLASSIFICATION PIPELINE")
    print("=" * 60)
    
    try:
        from image_classifier import ImageClassifier
        
        classifier = ImageClassifier(use_ml=False)
        
        # Step 1: Organize images
        print("\n[1/3] Organizing images into categories...")
        results = classifier.organize_images()
        
        # Step 2: Save report
        print("\n[2/3] Saving classification report...")
        report = classifier.save_classification_report(results)
        
        # Step 3: Show summary
        print("\n[3/3] Classification summary...")
        classifier.generate_summary(report)
        
        print(f"\n✅ Image classification completed: {report['successfully_classified']} images classified")
        return True
        
    except Exception as e:
        print(f"❌ Image classification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_data_search():
    """Run data search pipeline"""
    print("\n" + "=" * 60)
    print("DATA SEARCH PIPELINE")
    print("=" * 60)
    
    try:
        from perplexity_search import PerplexitySearch
        
        searcher = PerplexitySearch()
        
        queries = [
            "Arduino Uno pinout diagram",
            "Arduino programming tutorial",
            "Arduino components guide",
            "Arduino circuit examples"
        ]
        
        all_results = []
        print(f"Searching {len(queries)} queries...")
        
        for i, query in enumerate(queries, 1):
            print(f"  [{i}/{len(queries)}] {query}")
            results = searcher.search_arduino_topics(query, num_results=3)
            all_results.extend(results)
        
        # Save results
        output_file = searcher.save_results(all_results, "search_data.json")
        print(f"\n✅ Search completed: {len(all_results)} results saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Data search failed: {e}")
        return False

def run_data_classification():
    """Run text data classification"""
    print("\n" + "=" * 60)
    print("TEXT CLASSIFICATION PIPELINE")
    print("=" * 60)
    
    try:
        from llm_classifier import LLMClassifier
        
        # Check for OpenAI API key
        use_openai = False
        if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_key_here":
            use_openai = True
            print("Using OpenAI API for classification")
        else:
            print("Using keyword-based classification")
        
        classifier = LLMClassifier(use_openai=use_openai, api_key=Config.OPENAI_API_KEY)
        
        # Classify data
        output_file = classifier.process_data_file("search_data.json", "classified_text.json")
        
        if output_file:
            print(f"\n✅ Text classification completed: {output_file}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Text classification failed: {e}")
        return False

def run_comparison_analysis():
    """Run comparison analysis"""
    print("\n" + "=" * 60)
    print("COMPARISON ANALYSIS PIPELINE")
    print("=" * 60)
    
    try:
        from comparison_tool import DataComparer
        
        comparer = DataComparer()
        
        print("Comparing data sources...")
        comparison = comparer.compare_categories()
        
        print(f"\n✅ Comparison completed")
        print(f"   Scraper data: {comparison['scraper_data']['total_items']} items")
        print(f"   LLM data: {comparison['llm_data']['total_items']} items")
        print(f"   Common categories: {len(comparison['comparison']['common_categories'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Comparison analysis failed: {e}")
        return False

def generate_final_report():
    """Generate final comprehensive report"""
    print("\n" + "=" * 60)
    print("FINAL REPORT GENERATION")
    print("=" * 60)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = {
        "project": "SmartMentor Arduino Guide System",
        "timestamp": timestamp,
        "pipeline_version": "2.0",
        "components": {
            "image_collection": "✅" if Path("data/image_sources/image_report.json").exists() else "❌",
            "image_classification": "✅" if Path("data/image_sources/classification_report.json").exists() else "❌",
            "data_search": "✅" if Path("data/raw/search_data.json").exists() else "❌",
            "text_classification": "✅" if Path("data/processed/classified_text.json").exists() else "❌",
            "comparison_analysis": "✅" if Path("data/processed/comparison_results.json").exists() else "❌"
        },
        "statistics": {},
        "files_generated": []
    }
    
    # Collect statistics
    if Path("data/image_sources/image_report.json").exists():
        with open("data/image_sources/image_report.json", "r") as f:
            image_report = json.load(f)
            report["statistics"]["total_images"] = image_report["summary"]["total_images"]
    
    if Path("data/image_sources/classification_report.json").exists():
        with open("data/image_sources/classification_report.json", "r") as f:
            class_report = json.load(f)
            report["statistics"]["classified_images"] = class_report["successfully_classified"]
    
    # List all generated files
    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith(".json") or file.endswith(".txt"):
                full_path = Path(root) / file
                report["files_generated"].append(str(full_path.relative_to("data")))
    
    # Save final report
    report_file = "data/final_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=4)
    
    print("\n📋 FINAL REPORT SUMMARY")
    print("=" * 40)
    
    for component, status in report["components"].items():
        print(f"{component.replace('_', ' ').title()}: {status}")
    
    print("\n📊 STATISTICS")
    print("=" * 40)
    for stat, value in report["statistics"].items():
        print(f"{stat.replace('_', ' ').title()}: {value}")
    
    print(f"\n📁 Report saved to: {report_file}")
    print("=" * 60)
    
    return report

def main():
    """Main execution function"""
    print("\n" + "=" * 60)
    print("SMARTMENTOR ARDUINO PROJECT - COMPLETE PIPELINE")
    print("=" * 60)
    print(f"Start Time: {datetime.datetime.now()}")
    
    # Ensure directories
    ensure_directories()
    
    # Run pipelines
    pipelines = [
        ("Image Collection", run_image_collection),
        ("Image Classification", run_image_classification),
        ("Data Search", run_data_search),
        ("Text Classification", run_data_classification),
        ("Comparison Analysis", run_comparison_analysis)
    ]
    
    results = []
    
    for name, pipeline_func in pipelines:
        print(f"\n▶️  Running: {name}")
        success = pipeline_func()
        results.append((name, success))
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Generate final report
    print("\n" + "=" * 60)
    print("GENERATING FINAL REPORT")
    print("=" * 60)
    
    final_report = generate_final_report()
    
    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Successful pipelines: {successful}/{total}")
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {name}")
    
    print("\n" + "=" * 60)
    print("🎯 EXECUTION COMPLETED")
    print("=" * 60)
    print(f"End Time: {datetime.datetime.now()}")
    print(f"Total files generated: {len(final_report['files_generated'])}")
    print("Check the 'data/' directory for all output files")
    print("=" * 60)

if __name__ == "__main__":
    main()