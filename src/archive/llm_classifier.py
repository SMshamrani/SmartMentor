# src/llm_classifier.py
import os
import json
import re

class LLMClassifier:
    def __init__(self, use_openai=False, api_key=None):
        """يمكن استقبال use_openai و api_key أو لا"""
        self.use_openai = use_openai
        self.api_key = api_key
        
        if use_openai and api_key:
            try:
                import openai
                openai.api_key = api_key
                self.openai = openai
            except ImportError:
                print("⚠️ OpenAI library not installed. Falling back to keyword classification.")
                self.use_openai = False
                self.openai = None
        else:
            self.openai = None
        
        # قاعدة معرفة محلية للتصنيف
        self.keyword_categories = {
            "Pin Definitions": ["pin", "pinout", "gpio", "digital", "analog", "pwm", "i2c", "spi", "uart", "tx", "rx", "vcc", "gnd"],
            "Programming Instructions": ["code", "program", "sketch", "void setup", "void loop", "function", "library", "digitalwrite", "analogread", "serial.begin"],
            "Component Descriptions": ["sensor", "led", "resistor", "capacitor", "motor", "display", "module", "transistor", "diode", "breadboard", "jumper"],
            "Troubleshooting Tips": ["error", "problem", "fix", "debug", "solution", "issue", "won't work", "not working", "failed", "check", "verify"]
        }
    
    def classify_with_keywords(self, text):
        """يصّنف النص بناءً على الكلمات المفتاحية"""
        if not text:
            return "Other", 0.0
            
        text_lower = text.lower()
        
        category_scores = {}
        for category, keywords in self.keyword_categories.items():
            score = 0
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    score += 2
                elif keyword in text_lower:
                    score += 1
            
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            # اختر الفئة بأعلى درجة
            best_category = max(category_scores.items(), key=lambda x: x[1])[0]
            max_possible = len(self.keyword_categories[best_category]) * 2
            confidence = min(category_scores[best_category] / max_possible, 1.0)
        else:
            best_category = "Other"
            confidence = 0.0
        
        return best_category, confidence
    
    def classify_with_openai(self, text):
        """يصّنف النص باستخدام OpenAI API"""
        try:
            prompt = f"""
            Classify the following Arduino-related text into exactly one of these categories:
            - Pin Definitions
            - Programming Instructions  
            - Component Descriptions
            - Troubleshooting Tips
            - Other
            
            Text: "{text[:500]}"
            
            Respond ONLY with the category name.
            """
            
            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            
            category = response.choices[0].message.content.strip()
            return category, 0.9
            
        except Exception as e:
            print(f"  OpenAI error: {e}")
            return self.classify_with_keywords(text)
    
    def classify_text(self, text):
        """يصّنف النص باستخدام الطريقة المناسبة"""
        if not text or len(text.strip()) < 10:
            return "Other", 0.0
        
        if self.use_openai and self.openai:
            return self.classify_with_openai(text)
        else:
            return self.classify_with_keywords(text)
    
    def process_data_file(self, input_filename, output_filename="llm_classified.json"):
        """يعالج ملف البيانات ويصنفه"""
        input_path = os.path.join("data", "raw", input_filename)
        output_path = os.path.join("data", "processed", output_filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if not os.path.exists(input_path):
            print(f"  ⚠️ ملف الإدخال غير موجود: {input_path}")
            # إنشاء بيانات اختبار
            test_data = [
                {"title": "Arduino Uno Guide", "snippet": "Pinout diagram and pin functions for Arduino Uno"},
                {"title": "LED Blink Code", "snippet": "How to program Arduino to make LED blink using digitalWrite"}
            ]
            with open(input_path, "w") as f:
                json.dump(test_data, f, indent=2)
            print(f"  ✅ تم إنشاء بيانات اختبار في {input_path}")
        
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"  📄 جاري تصنيف {len(data)} عنصر...")
        
        classified_data = []
        for idx, item in enumerate(data):
            text = ""
            if isinstance(item, dict):
                if "snippet" in item and item["snippet"]:
                    text = item["snippet"]
                elif "title" in item and item["title"]:
                    text = item["title"]
                elif "description" in item:
                    text = item["description"]
            elif isinstance(item, str):
                text = item
            
            category, confidence = self.classify_text(text)
            
            classified_item = {
                "id": idx + 1,
                "original": item,
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "category": category,
                "confidence": round(confidence, 2),
                "source": "perplexity_search",
                "classification_method": "openai" if self.use_openai else "keyword_based"
            }
            
            classified_data.append(classified_item)
            
            if (idx + 1) % 5 == 0:
                print(f"    ... تم تصنيف {idx + 1}/{len(data)}")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(classified_data, f, indent=4, ensure_ascii=False)
        
        print(f"  ✅ تم حفظ البيانات المصنفة في: {output_path}")
        
        # إحصائيات التصنيف
        self.print_statistics(classified_data)
        
        return output_path
    
    def print_statistics(self, data):
        """يطبع إحصائيات التصنيف"""
        from collections import Counter
        
        categories = [item["category"] for item in data]
        category_counts = Counter(categories)
        
        print(f"\n  📊 إحصائيات التصنيف:")
        print(f"  {'-'*30}")
        for category, count in category_counts.most_common():
            percentage = (count / len(data)) * 100
            print(f"  {category}: {count} ({percentage:.1f}%)")
        print(f"  {'-'*30}")
        print(f"  الإجمالي: {len(data)} عنصر")

# دالة اختبار
def test_classification():
    classifier = LLMClassifier()  # بدون وسائط
    
    test_texts = [
        "Arduino Uno has 14 digital pins and 6 analog inputs",
        "To make an LED blink, use the digitalWrite() function in the loop",
        "Connect a 220 ohm resistor in series with the LED",
        "If your Arduino is not detected, check the USB cable connection"
    ]
    
    for text in test_texts:
        category, confidence = classifier.classify_text(text)
        print(f"النص: {text[:50]}...")
        print(f"  الفئة: {category} (ثقة: {confidence:.2f})")
        print()

if __name__ == "__main__":
    test_classification()