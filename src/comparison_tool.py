# src/comparison_tool.py
import json
import os
from collections import Counter

class DataComparer:
    def __init__(self):
        self.scraper_path = os.path.join("data", "scraped_json", "comprehensive_arduino_data.json")
        self.llm_path = os.path.join("data", "processed", "llm_classified.json")
    
    def create_sample_scraper_data(self):
        """ينشئ بيانات سكريبر وهمية"""
        sample_scraper_data = [
            {
                "component": "Arduino Uno",
                "type": "board",
                "description": "The most common Arduino board with 14 digital I/O pins and 6 analog inputs",
                "category": "Pin Definitions",
                "source": "scraper"
            },
            {
                "component": "LED Blink Tutorial",
                "type": "tutorial", 
                "description": "Learn how to make an LED blink with Arduino programming using digitalWrite function",
                "category": "Programming Instructions",
                "source": "scraper"
            },
            {
                "component": "Resistor",
                "type": "component",
                "description": "Electronic component used to limit current in circuits, essential for protecting LEDs",
                "category": "Component Descriptions", 
                "source": "scraper"
            },
            {
                "component": "Arduino Not Detected Fix",
                "type": "troubleshooting",
                "description": "Solutions for when Arduino is not detected by computer: check drivers, USB cable, and port selection",
                "category": "Troubleshooting Tips",
                "source": "scraper"
            }
        ]
        
        os.makedirs(os.path.dirname(self.scraper_path), exist_ok=True)
        with open(self.scraper_path, "w", encoding="utf-8") as f:
            json.dump(sample_scraper_data, f, indent=4)
        
        print(f"  ✅ تم إنشاء بيانات سكريبر وهمية في: {self.scraper_path}")
        return sample_scraper_data
    
    def load_or_create_data(self):
        """يحمّل البيانات أو ينشئها إذا لم تكن موجودة"""
        # تحميل أو إنشاء بيانات السكريبر
        if os.path.exists(self.scraper_path):
            with open(self.scraper_path, "r", encoding="utf-8") as f:
                scraper_data = json.load(f)
            print(f"  📁 تم تحميل {len(scraper_data)} عنصر من بيانات السكريبر")
        else:
            print(f"  ⚠️ ملف السكريبر غير موجود: {self.scraper_path}")
            scraper_data = self.create_sample_scraper_data()
        
        # تحميل بيانات LLM
        if os.path.exists(self.llm_path):
            with open(self.llm_path, "r", encoding="utf-8") as f:
                llm_data = json.load(f)
            print(f"  📁 تم تحميل {len(llm_data)} عنصر من بيانات LLM")
        else:
            print(f"  ⚠️ ملف LLM غير موجود: {self.llm_path}")
            # إنشاء بيانات LLM وهمية
            llm_data = [
                {
                    "id": 1,
                    "original": {"title": "Arduino Pinout Guide", "snippet": "Complete guide to Arduino pins and their functions"},
                    "category": "Pin Definitions",
                    "source": "perplexity_search"
                },
                {
                    "id": 2, 
                    "original": {"title": "How to Program Arduino", "snippet": "Step by step programming tutorial for beginners"},
                    "category": "Programming Instructions",
                    "source": "perplexity_search"
                },
                {
                    "id": 3,
                    "original": {"title": "Arduino Components List", "snippet": "List of essential Arduino components and sensors for projects"},
                    "category": "Component Descriptions",
                    "source": "perplexity_search"
                }
            ]
            
            os.makedirs(os.path.dirname(self.llm_path), exist_ok=True)
            with open(self.llm_path, "w", encoding="utf-8") as f:
                json.dump(llm_data, f, indent=4)
            
            print(f"  ✅ تم إنشاء بيانات LLM وهمية في: {self.llm_path}")
        
        return scraper_data, llm_data
    
    def compare_categories(self):
        """يقارن توزيع الفئات بين مصادر البيانات"""
        print("  جاري تحميل البيانات للمقارنة...")
        scraper_data, llm_data = self.load_or_create_data()
        
        # استخراج الفئات
        scraper_categories = []
        for item in scraper_data:
            if isinstance(item, dict):
                scraper_categories.append(item.get("category", "Unknown"))
        
        llm_categories = []
        for item in llm_data:
            if isinstance(item, dict):
                llm_categories.append(item.get("category", "Unknown"))
        
        scraper_counts = Counter(scraper_categories)
        llm_counts = Counter(llm_categories)
        
        comparison = {
            "scraper_data": {
                "total_items": len(scraper_data),
                "categories": dict(scraper_counts),
                "category_distribution": {
                    cat: f"{(count/len(scraper_data))*100:.1f}%"
                    for cat, count in scraper_counts.items()
                }
            },
            "llm_data": {
                "total_items": len(llm_data),
                "categories": dict(llm_counts),
                "category_distribution": {
                    cat: f"{(count/len(llm_data))*100:.1f}%"
                    for cat, count in llm_counts.items()
                }
            },
            "comparison": {
                "common_categories": list(set(scraper_categories) & set(llm_categories)),
                "unique_to_scraper": list(set(scraper_categories) - set(llm_categories)),
                "unique_to_llm": list(set(llm_categories) - set(scraper_categories)),
                "total_overlap": len(set(scraper_categories) & set(llm_categories))
            }
        }
        
        output_path = os.path.join("data", "processed", "comparison_results.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=4, ensure_ascii=False)
        
        print(f"  ✅ تم حفظ نتائج المقارنة في: {output_path}")
        
        self.print_comparison_summary(comparison)
        
        return comparison
    
    def print_comparison_summary(self, comparison):
        """يطبع ملخص المقارنة"""
        print(f"\n  📊 ملخص المقارنة:")
        print(f"  {'='*40}")
        
        print(f"  بيانات السكريبر:")
        print(f"    - العدد الإجمالي: {comparison['scraper_data']['total_items']}")
        for cat, count in comparison['scraper_data']['categories'].items():
            print(f"    - {cat}: {count} ({comparison['scraper_data']['category_distribution'][cat]})")
        
        print(f"\n  بيانات LLM:")
        print(f"    - العدد الإجمالي: {comparison['llm_data']['total_items']}")
        for cat, count in comparison['llm_data']['categories'].items():
            print(f"    - {cat}: {count} ({comparison['llm_data']['category_distribution'][cat]})")
        
        print(f"\n  المقارنة:")
        print(f"    - الفئات المشتركة: {', '.join(comparison['comparison']['common_categories'])}")
        print(f"    - فئات خاصة بالسكريبر: {', '.join(comparison['comparison']['unique_to_scraper'])}")
        print(f"    - فئات خاصة بـ LLM: {', '.join(comparison['comparison']['unique_to_llm'])}")
        print(f"    - عدد الفئات المتداخلة: {comparison['comparison']['total_overlap']}")
        
        print(f"  {'='*40}")

# دالة اختبار
def test_comparison():
    comparer = DataComparer()
    results = comparer.compare_categories()
    print("\n✅ تم إكمال المقارنة بنجاح")

if __name__ == "__main__":
    test_comparison()