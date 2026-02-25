# src/Phase1_OfflineProcessing/data_loader.py

import json
from pathlib import Path

import pandas as pd


class DataLoader:
    """Load raw Arduino UNO data from XLSX and CSV, then convert it to structured JSON."""

    def __init__(self):
        # Path to raw scraped data (XLSX and CSV files)
        self.raw_path = Path("data/raw/scraped_data")
        # Path to store processed JSON output
        self.processed_path = Path("data/processed")

    def load_xlsx_csv(self):
        """Load XLSX and CSV files, merge them, clean them, and convert to JSON."""

        # Read XLSX file
        df_xlsx = pd.read_excel(
            self.raw_path / "arduino_uno_raw.xlsx"
        )

        # Read CSV file
        df_csv = pd.read_csv(
            self.raw_path / "arduino_uno_raw.csv"
        )

        # Merge data from both sources into a single DataFrame
        combined_data = pd.concat([df_xlsx, df_csv], ignore_index=True)

        # Basic cleaning: remove duplicate rows
        combined_data = combined_data.drop_duplicates()

        # Convert DataFrame into a structured Python dictionary
        structured_data = self.structure_data(combined_data)

        # Save structured data as JSON file
        self.save_json(structured_data)

        return structured_data

    def structure_data(self, df):
        """Transform the DataFrame into a logical device-centered JSON structure."""

        # Base structure for Arduino UNO R3 device
        structured = {
            "device": {
                "name": "Arduino UNO R3",
                "description": "Microcontroller board based on ATmega328P",
                "official_link": "https://docs.arduino.cc/tutorials/uno-rev3/getting-started/",
                "specifications": {},
                "components": [],
                "pinout": {},
                "tutorials": []
            }
        }

        # Populate structure based on column names
        for col in df.columns:
            col_lower = col.lower()

            # Pin-related columns go into pinout section
            if "pin" in col_lower:
                structured["device"]["pinout"][col] = df[col].tolist()

            # Component-related columns go into components list
            elif "component" in col_lower:
                structured["device"]["components"].append(df[col].tolist())

            # Specification-related columns go into specifications
            elif "spec" in col_lower:
                structured["device"]["specifications"][col] = df[col].tolist()

            # Tutorial-related columns go into tutorials list
            elif "tutorial" in col_lower:
                structured["device"]["tutorials"].append(df[col].tolist())

        return structured

    def save_json(self, data):
        """Save the structured data dictionary as a JSON file."""
        output_file = self.processed_path / "arduino_uno_structured.json"

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON with UTF-8 encoding and indentation for readability
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved structured data to: {output_file}")


# Example usage (can be removed or kept for manual testing)
if __name__ == "__main__":
    loader = DataLoader()
    data = loader.load_xlsx_csv()
    print(data)
