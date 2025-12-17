# data/raw/README_raw.md

## Raw Data Description

### Source 1: Instant Data Scraper
- **Files:** 
  - `arduino_uno_raw.xlsx` - البيانات بصيغة جدول
  - `arduino_uno_raw.csv` - البيانات بصيغة نصية
- **Source:** https://docs.arduino.cc/tutorials/uno-rev3/getting-started/
- **Date:** 2025-12-10
- **Content:** مواصفات Arduino UNO، الدبابيس، المكونات

### Source 2: Scraped Images
- **Official Documentation Images:** من arduino.cc و wikimedia
- **Components:** صور المكونات الشائعة (LED, Resistor, etc)
- **Wiring Diagrams:** رسوم التوصيل التوضيحية

## Processing Steps
1. ✅ Load XLSX/CSV
2. ✅ Download images from official sources
3. ✅ Enrich with Perplexity
4. ✅ Structure data into JSON
5. ✅ Store in processed/
