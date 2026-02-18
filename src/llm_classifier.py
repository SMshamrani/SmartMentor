import json
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_client import ask_llm

CLASS_LABELS = [
    "pinout_diagram", 
    "components_guide", 
    "basic_tutorial", 
    "advanced_project", 
    "troubleshooting", 
    "other"
]

SYSTEM_MESSAGE = """
You are a classifier for an Arduino learning dataset.
Given a short title and snippet, assign exactly ONE category from this list:
- pinout_diagram
- components_guide
- basic_tutorial
- advanced_project
- troubleshooting
- other

Return only the category name, nothing else. No explanations.
"""

def classify_item(title, snippet):
    prompt = f"Title: {title}\nSnippet: {snippet}\nCategory:"
    raw_label = ask_llm(prompt, system_message=SYSTEM_MESSAGE, max_tokens=16)
    label = raw_label.strip().lower()
    
    # Fuzzy matching to handle minor variations
    for valid_label in CLASS_LABELS:
        if valid_label in label:
            return valid_label
    return "other"

if __name__ == "__main__":
    print("Testing LLM classification...")
    test_cases = [
        ("Arduino UNO pinout", "Learn about digital and analog pins of Arduino UNO"),
        ("LED blinking tutorial", "First Arduino project for beginners"),
        ("Fix Arduino not uploading", "Troubleshooting common upload errors"),
    ]
    
    for title, snippet in test_cases:
        prediction = classify_item(title, snippet)
        print(f"Input: {title}")
        print(f"Snippet: {snippet}")
        print(f"Predicted: {prediction}")
        print("-" * 50)
