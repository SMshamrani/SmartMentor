# src/perplexity_search.py
import os
import json
import time

class PerplexitySearch:
    def __init__(self):
        """بدون حاجة لـ api_key"""
        pass

    def search_arduino_topics(self, query, num_results=5):
        """يبحث عن مواضيع Arduino باستخدام بحث وهمي للاختبار"""
        print(f"  [وهمي] جاري البحث عن: '{query}'")
        
        # بيانات وهمية للاختبار
        mock_results = self.get_mock_results(query, num_results)
        return mock_results

    def get_mock_results(self, query, num_results):
        """ينشئ بيانات وهمية للاختبار"""
        mock_templates = {
            "Arduino Uno pinout diagram": [
                {
                    "title": "Arduino Uno R3 Pinout Diagram - Complete Guide",
                    "snippet": "Detailed pinout diagram showing all 14 digital pins, 6 analog inputs, power pins, and communication interfaces on Arduino Uno R3 board.",
                    "link": "https://docs.arduino.cc/hardware/uno-rev3",
                    "position": 1
                },
                {
                    "title": "Understanding Arduino Uno Pin Configuration",
                    "snippet": "Learn about each pin function on Arduino Uno: digital I/O, PWM, analog inputs, and communication protocols like I2C and SPI.",
                    "link": "https://www.arduino.cc/en/Tutorial/Foundations/AnalogInputPins",
                    "position": 2
                }
            ],
            "Arduino programming for beginners": [
                {
                    "title": "Arduino Programming for Complete Beginners",
                    "snippet": "Step-by-step guide to start programming Arduino. Learn basic syntax, functions, and upload your first sketch to control LEDs.",
                    "link": "https://www.arduino.cc/en/Guide/HomePage",
                    "position": 1
                },
                {
                    "title": "Getting Started with Arduino IDE",
                    "snippet": "How to install Arduino IDE, write your first program, and upload code to Arduino board with simple LED blink example.",
                    "link": "https://create.arduino.cc/projecthub/Arduino_Genuino/getting-started-with-arduino-web-editor-on-various-platforms-4b3e4a",
                    "position": 2
                }
            ],
            "Arduino components and sensors": [
                {
                    "title": "Essential Arduino Components for Projects",
                    "snippet": "List of must-have components: resistors, LEDs, breadboard, jumper wires, sensors (temperature, motion, light), and actuators.",
                    "link": "https://learn.sparkfun.com/tutorials/arduino-components/all",
                    "position": 1
                },
                {
                    "title": "Arduino Sensors Guide - How to Use Different Sensors",
                    "snippet": "Comprehensive guide to using various sensors with Arduino: ultrasonic, temperature, humidity, IR, and motion sensors.",
                    "link": "https://www.instructables.com/Arduino-Sensors/",
                    "position": 2
                }
            ],
            "Arduino troubleshooting common problems": [
                {
                    "title": "Common Arduino Problems and Solutions",
                    "snippet": "Troubleshooting guide for frequent Arduino issues: board not detected, upload errors, serial communication problems, and power issues.",
                    "link": "https://support.arduino.cc/hc/en-us/articles/4402996340114-Troubleshooting-guide",
                    "position": 1
                },
                {
                    "title": "Arduino Troubleshooting Checklist",
                    "snippet": "Step-by-step checklist to diagnose and fix common Arduino problems including driver issues, port selection, and code errors.",
                    "link": "https://forum.arduino.cc/t/arduino-troubleshooting-guide/420823",
                    "position": 2
                }
            ]
        }
        
        if query in mock_templates:
            return mock_templates[query][:num_results]
        else:
            return [
                {
                    "title": f"Search result for: {query}",
                    "snippet": f"This is sample data for the query: {query}. In real scenario, this would be actual search result.",
                    "link": "https://example.com",
                    "position": i+1,
                    "query": query
                }
                for i in range(num_results)
            ]

    def save_results(self, results, filename="perplexity_results.json"):
        """يحفظ النتائج في ملف JSON"""
        output_path = os.path.join("data", "raw", filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        print(f"  ✅ تم حفظ {len(results)} نتيجة في: {output_path}")
        return output_path

# دالة اختبار
def test_search():
    searcher = PerplexitySearch()
    queries = ["Arduino Uno pinout", "Arduino LED blink tutorial"]
    
    all_results = []
    for query in queries:
        print(f"\nجاري البحث عن: {query}")
        results = searcher.search_arduino_topics(query, num_results=3)
        all_results.extend(results)
        time.sleep(1)  # تجنب الحظر
    
    searcher.save_results(all_results, "test_search_results.json")
    print(f"\n✅ تم جمع {len(all_results)} نتيجة بنجاح")

if __name__ == "__main__":
    test_search()