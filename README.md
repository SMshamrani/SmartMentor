SmartMentor Arduino Guide System is an educational data pipeline built around the Arduino UNO R3, designed as part of a graduation project. It focuses on transforming scraped reference data and images into clean, structured resources that can support guide-style and future intelligent mentoring applications.

## Project Overview

SmartMentor aims to bridge the gap between traditional device manuals and practical, hands-on guidance by organizing and preparing high‑quality reference data about Arduino UNO R3. The current repository focuses on Phase 1 of the system: offline processing of structured tabular data and curated visual resources. Future extensions can integrate this data into an AI‑powered mobile app for interactive assistance.

The system is implemented as a reproducible Python pipeline with two primary parts:

- Phase 1: Offline data processing (scraped XLSX/CSV → structured JSON + SQL).
- Image setup: Downloading and generating Arduino‑related images and metadata.

Repository URL:  
`https://github.com/SMshamrani/SmartMentor`

## Features

- Load Arduino UNO reference data from XLSX and CSV files.
- Clean raw records and convert them into a device‑centered JSON structure.
- Map the data to a relational schema and generate SQL INSERT statements.
- Download real Arduino board, component, and pinout images from open sources.
- Generate realistic mock images when online images are unavailable.
- Build a metadata file summarizing all images (paths, size, dimensions, category).
- Include optional experimental pipelines for image classification, web search, and LLM‑based text classification (kept separate from the core Phase 1 flow).

## Project Structure

```text
SmartMentor/
├── main.py                      # Entry point for Phase 1 data pipeline
├── setup_images.py              # Image setup: download/generate images + metadata
├── config.py                    # Configuration (DB, paths, API keys via .env)
├── requirements.txt             # Python dependencies
├── database/
│   └── schema.sql               # PostgreSQL schema (Users, Devices, Guides, Steps, etc.)
├── src/
│   ├── Phase1_OfflineProcessing/
│   │   ├── data_loader.py               # Load XLSX/CSV and build structured JSON
│   │   ├── enhanced_data_cleaner.py     # Clean/map data and generate SQL + reports
│   │   ├── web_scraper_images.py        # Scrape images from Arduino Docs (optional)
│   │   └── arduino_project_image_scraper.py  # Scrape example project images (optional)
│   └── database_handler.py      # Optional: database connection and inserts
├── scripts/
│   └── setup_data.py            # Legacy/extended data setup (experimental)
├── data/
│   ├── raw/                     # Raw input files (XLSX, CSV, scraped JSON)
│   ├── processed/               # Processed JSON and text outputs
│   ├── scraped_images/          # Downloaded + generated images
│   ├── classified_images/       # (Optional) classified images by category
│   ├── image_sources/           # Image reports and classification summaries
│   └── outputs/                 # SQL scripts and summary reports
└── archive/                     # (Optional) experimental or legacy scripts
```

## Installation

Clone the repository:

```bash
git clone https://github.com/SMshamrani/SmartMentor.git
cd SmartMentor
```

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root (optional, for database/API configuration):

```text
DB_NAME=arduino_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Optional for experimental LLM / search modules
OPENAI_API_KEY=your_openai_key_here
SERPAPI_KEY=your_serpapi_key_here
```

## Usage

### 1. Phase 1 Data Pipeline

This pipeline loads raw tabular data about Arduino UNO from XLSX/CSV files and converts it into structured JSON.

Run:

```bash
python main.py
```

This will:

- Read `data/raw/scraped_data/arduino_uno_raw.xlsx`
- Read `data/raw/scraped_data/arduino_uno_raw.csv`
- Merge and de‑duplicate rows
- Produce `data/processed/arduino_uno_structured.json`

To run the enhanced cleaning, mapping, and SQL generation:

```bash
python -m src.Phase1_OfflineProcessing.enhanced_data_cleaner
```

This script will:

- Clean and normalize the raw data.
- Map it into a schema‑like structure (`Devices`, `Components`, `Guides`, `Steps`).
- Save:
  - `data/processed/cleaned_data_enhanced.json`
  - `data/outputs/database_inserts_complete.sql`
  - `data/outputs/data_cleaning_summary_enhanced.json`

### 2. Image Setup Pipeline

This pipeline prepares the visual resources used in the project (real images + generated mockups + metadata).

Run:

```bash
python setup_images.py
```

It will:

- Create all required image directories under `data/scraped_images/` and `data/classified_images/`.
- Attempt to download real Arduino board, component, and pinout images.
- If downloads fail, generate realistic board/component/pinout mock images.
- Copy any existing images from common project folders into the unified structure.
- Build `data/scraped_images/metadata.json` with per‑image metadata and category counts.

### 3. Optional / Experimental Pipelines

These scripts are not required for the core Phase 1 pipeline but are included for experimentation and future work:

- `scripts/setup_data.py`: extended data setup (data loading + GitHub images + Arduino Docs scraping).
- `main_updated.py`: experimental full pipeline (image collection, classification, web search, LLM classification, comparison).
- `src/database_handler.py`: connect to PostgreSQL, create tables using `database/schema.sql`, and insert scraped / classified data.

If you use these components, ensure that:

- PostgreSQL is running with credentials matching your `.env` file or the default values.
- Optional APIs (OpenAI, SERPAPI) are configured when using LLM‑based modules.

## Database Schema

The database schema is defined in `database/schema.sql` and includes the following main tables:

- `Users`: future user accounts for authentication and progress tracking.
- `Devices`: Arduino boards and similar hardware devices.
- `Components`: electronic components associated with each device.
- `Guides`: tutorials or learning paths per device.
- `Steps`: step‑by‑step instructions inside each guide.
- `UserProgress`: tracks a user’s progress through guides and steps.
- `Feedback`: user ratings and comments associated with guides.

The `enhanced_data_cleaner.py` script generates SQL INSERT statements aligned with this schema and writes them to `data/outputs/database_inserts_complete.sql` for easy database population.

## Configuration

Global configuration is centralized in `config.py`:

- Database connection parameters (read from environment variables with sensible defaults).
- Data directories (`data/raw`, `data/processed`, `data/scraped_images`).
- Optional API keys (`OPENAI_API_KEY`, `SERPAPI_KEY`) for experimental modules.

To ensure required data folders exist, you can call:

```python
from config import Config
Config.ensure_directories()
```

(Several scripts already perform this internally.)

## Requirements

Key dependencies include:

- `pandas`, `numpy` – data loading and processing.
- `openpyxl` – Excel file support for `pandas`.
- `requests`, `beautifulsoup4`, `lxml` – web scraping utilities.
- `Pillow` – image verification and mock image generation.
- `python-dotenv` – environment variable loading from `.env`.

Optional dependencies for extended functionality:

- `psycopg2-binary`, `sqlalchemy` – PostgreSQL integration.
- `openai`, `googlesearch-python`, `selenium`, `opencv-python`, `scikit-image` – experimental LLM, search, and advanced image processing.

All dependencies are listed in `requirements.txt`.

## Running Tests (Optional)

If you add or maintain tests, they can be executed with:

```bash
pytest
```

Ensure that your virtual environment is active and all required dependencies are installed.

## Contributors

This project was developed as a graduation project by:

- Student 1 – Sarah Mohammad Alshamrani   444003567 
- Student 2 – Waad Mohammad AL luhaybi   444001927 
- Student 3 – Shahad Hassan Altalhi    444001817
- Student 4 – Reem Ahmad Alharbi   444003905
  
- Supervisor: Dr. Daren FadolAlkarim


## License

This project is licensed under the MIT License.  
See the `LICENSE` file in the repository root for full license text.
