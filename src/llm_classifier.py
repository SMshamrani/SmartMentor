import json
from pathlib import Path
from src.llm_client import ask_llm

CLASS_LABELS = ["pinout_diagram", "components_guide", "basic_tutorial", "advanced_project", "troubleshooting", "other"]

SYSTEM_MESSAGE = """
You are a classifier for an Arduino learning dataset.
Given a short title and snippet, assign exactly ONE category from this list:
- pinout_diagram
- components_guide
- basic_tutorial
- advanced_project
- troubleshooting
- other
Return only the category name, nothing else.
"""

def classify_item(title, snippet):
    prompt = f"Title: {title}\nSnippet: {snippet}\nLabel:"
    raw_label = ask_llm(prompt, system_message=SYSTEM_MESSAGE, max_tokens=16)
    label = raw_label.strip()
    return label if label in CLASS_LABELS else "other"

if __name__ == "__main__":
    from config import Config
    print("Testing LLM classification...")
    title = "Arduino UNO pinout"
    snippet = "Learn about digital and analog pins of Arduino UNO"
    print(f"Input: {title}")
    print(f"Snippet: {snippet}")
    print(f"Predicted: {classify_item(title, snippet)}")
