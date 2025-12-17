# main_updated.py
"""
Updated main pipeline for the SmartMentor Arduino project.
Includes image collection, classification, web search, text classification, and comparison.
"""

import datetime
import json
import os
import sys
from pathlib import Path

# Add src directory to Python path to allow local imports
sys.path.append(str(Path(__file__).parent / "src"))

from config import Config


def ensure_directories():
    """Ensure that all required data directories exist."""
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
        "data/image_sources",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("All directories created")


def run_image_collection():
    """Run the image collection sub-pipeline (download and catalog images)."""
    print("\n" + "=" * 60)
    print("IMAGE COLLECTION PIPELINE")
    print("=" * 60)

    try:
        from image_collector import ImageCollector

        collector = ImageCollector()

        # Step 1: Download sample images
        print("\n[1/3] Downloading Arduino images...")
        downloaded = collector.download_sample_images()

        # Step 2: Create image catalog
        print("\n[2/3] Creating image catalog...")
        catalog = collector.create_image_catalog()

        # Step 3: Generate image report JSON
        print("\n[3/3] Generating image report...")
        report = collector.generate_image_report()

        print(
            f"\nImage collection completed: "
            f"{report['summary']['total_images']} images"
        )
        return True

    except Exception as e:
        print(f"Image collection failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_image_classification():
    """Run the image classification sub-pipeline (rule-based or ML-based)."""
    print("\n" + "=" * 60)
    print("IMAGE CLASSIFICATION PIPELINE")
    print("=" * 60)

    try:
        from image_classifier import ImageClassifier

        # use_ml=False means using heuristic/keyword-based classification
        classifier = ImageClassifier(use_ml=False)

        # Step 1: Organize images into category folders
        print("\n[1/3] Organizing images into categories...")
        results = classifier.organize_images()

        # Step 2: Save classification report as JSON
        print("\n[2/3] Saving classification report...")
        report = classifier.save_classification_report(results)

        # Step 3: Print a summary to the console
        print("\n[3/3] Classification summary...")
        classifier.generate_summary(report)

        print(
            f"\nImage classification completed: "
            f"{report['successfully_classified']} images classified"
        )
        return True

    except Exception as e:
        print(f"Image classification failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_data_search():
    """Run the text data search sub-pipeline (Perplexity or similar search)."""
    print("\n" + "=" * 60)
    print("DATA SEARCH PIPELINE")
    print("=" * 60)

    try:
        from perplexity_search import PerplexitySearch

        searcher = PerplexitySearch()

        # Example queries related to Arduino UNO learning resources
        queries = [
            "Arduino Uno pinout diagram",
            "Arduino programming tutorial",
            "Arduino components guide",
            "Arduino circuit examples",
        ]

        all_results = []
        print(f"Searching {len(queries)} queries...")

        for i, query in enumerate(queries, start=1):
            print(f"  [{i}/{len(queries)}] {query}")
            results = searcher.search_arduino_topics(query, num_results=3)
            all_results.extend(results)

        # Save aggregated search results as JSON
        output_file = searcher.save_results(all_results, "search_data.json")
        print(
            f"\nSearch completed: {len(all_results)} results saved to {output_file}"
        )
        return True

    except Exception as e:
        print(f"Data search failed: {e}")
        return False


def run_data_classification():
    """Run the text classification sub-pipeline (LLM-based or keyword-based)."""
    print("\n" + "=" * 60)
    print("TEXT CLASSIFICATION PIPELINE")
    print("=" * 60)

    try:
        from llm_classifier import LLMClassifier

        # Decide whether to use OpenAI API based on config
        use_openai = False
        if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_key_here":
            use_openai = True
            print("Using OpenAI API for classification")
        else:
            print("Using keyword-based classification")

        classifier = LLMClassifier(
            use_openai=use_openai,
            api_key=Config.OPENAI_API_KEY,
        )

        # Classify search_data.json into structured categories
        output_file = classifier.process_data_file(
            "search_data.json", "classified_text.json"
        )

        if output_file:
            print(f"\nText classification completed: {output_file}")
            return True
        else:
            return False

    except Exception as e:
        print(f"Text classification failed: {e}")
        return False


def run_comparison_analysis():
    """Run comparison between scraper-based data and LLM-based data."""
    print("\n" + "=" * 60)
    print("COMPARISON ANALYSIS PIPELINE")
    print("=" * 60)

    try:
        from comparison_tool import DataComparer

        comparer = DataComparer()

        print("Comparing data sources...")
        comparison = comparer.compare_categories()

        print("\nComparison completed")
        print(f"   Scraper data: {comparison['scraper_data']['total_items']} items")
        print(f"   LLM data: {comparison['llm_data']['total_items']} items")
        print(
            f"   Common categories: "
            f"{len(comparison['comparison']['common_categories'])}"
        )

        return True

    except Exception as e:
        print(f"Comparison analysis failed: {e}")
        return False


def generate_final_report():
    """Generate a final JSON report summarizing all pipeline components."""
    print("\n" + "=" * 60)
    print("FINAL REPORT GENERATION")
    print("=" * 60)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = {
        "project": "SmartMentor Arduino Guide System",
        "timestamp": timestamp,
        "pipeline_version": "2.0",
        "components": {
            "image_collection": "OK"
            if Path("data/image_sources/image_report.json").exists()
            else "MISSING",
            "image_classification": "OK"
            if Path("data/image_sources/classification_report.json").exists()
            else "MISSING",
            "data_search": "OK"
            if Path("data/raw/search_data.json").exists()
            else "MISSING",
            "text_classification": "OK"
            if Path("data/processed/classified_text.json").exists()
            else "MISSING",
            "comparison_analysis": "OK"
            if Path("data/processed/comparison_results.json").exists()
            else "MISSING",
        },
        "statistics": {},
        "files_generated": [],
    }

    # Collect statistics from generated reports if they exist
    if Path("data/image_sources/image_report.json").exists():
        with open("data/image_sources/image_report.json", "r", encoding="utf-8") as f:
            image_report = json.load(f)
            report["statistics"]["total_images"] = image_report["summary"]["total_images"]

    if Path("data/image_sources/classification_report.json").exists():
        with open(
            "data/image_sources/classification_report.json",
            "r",
            encoding="utf-8",
        ) as f:
            class_report = json.load(f)
            report["statistics"]["classified_images"] = class_report[
                "successfully_classified"
            ]

    # List all JSON and text files under the data directory
    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith(".json") or file.endswith(".txt"):
                full_path = Path(root) / file
                report["files_generated"].append(str(full_path.relative_to("data")))

    # Save final report JSON
    report_file = "data/final_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("\nFINAL REPORT SUMMARY")
    print("=" * 40)

    for component, status in report["components"].items():
        print(f"{component.replace('_', ' ').title()}: {status}")

    print("\nSTATISTICS")
    print("=" * 40)
    for stat, value in report["statistics"].items():
        print(f"{stat.replace('_', ' ').title()}: {value}")

    print(f"\nReport saved to: {report_file}")
    print("=" * 60)

    return report


def main():
    """Main execution function for running the full experimental pipeline."""
    print("\n" + "=" * 60)
    print("SMARTMENTOR ARDUINO PROJECT - COMPLETE PIPELINE")
    print("=" * 60)
    print(f"Start Time: {datetime.datetime.now()}")

    # Ensure all necessary directories exist
    ensure_directories()

    # List of pipeline stages to run sequentially
    pipelines = [
        ("Image Collection", run_image_collection),
        ("Image Classification", run_image_classification),
        ("Data Search", run_data_search),
        ("Text Classification", run_data_classification),
        ("Comparison Analysis", run_comparison_analysis),
    ]

    results = []

    for name, pipeline_func in pipelines:
        print(f"\nRunning: {name}")
        success = pipeline_func()
        results.append((name, success))
        print(f"   Result: {'SUCCESS' if success else 'FAILED'}")

    # Generate overall final report
    print("\n" + "=" * 60)
    print("GENERATING FINAL REPORT")
    print("=" * 60)

    final_report = generate_final_report()

    # Summary of pipeline execution
    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 60)

    successful = sum(1 for _, success in results if success)
    total = len(results)

    print(f"Successful pipelines: {successful}/{total}")

    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  {status} - {name}")

    print("\n" + "=" * 60)
    print("EXECUTION COMPLETED")
    print("=" * 60)
    print(f"End Time: {datetime.datetime.now()}")
    print(f"Total files generated: {len(final_report['files_generated'])}")
    print("Check the 'data/' directory for all output files")
    print("=" * 60)


if __name__ == "__main__":
    main()
