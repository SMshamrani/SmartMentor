#!/usr/bin/env python3
"""
Enhanced data cleaning and mapping with component extraction for Arduino UNO data.
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd


class EnhancedDataCleaner:
    """Clean raw data, map it to a database-like schema, and generate JSON and SQL outputs."""

    def __init__(self):
        # Paths for raw input data and processed outputs
        self.raw_path = Path("data/raw/scraped_data")
        self.processed_path = Path("data/processed")
        self.output_path = Path("data/outputs")

        # Ensure output directories exist
        for path in [self.processed_path, self.output_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Storage for raw DataFrames and schema-mapped data
        self.data = {}
        self.schema_mapping = {
            "Devices": [],
            "Components": [],
            "Guides": [],
            "Steps": []
        }

    def load_raw_data(self):
        """Load raw CSV and XLSX data for Arduino UNO."""
        print("\nLoading raw data...")

        # Load CSV file if it exists
        csv_file = self.raw_path / "arduino_uno_raw.csv"
        if csv_file.exists():
            self.data["csv"] = pd.read_csv(csv_file)
            print(f"CSV loaded: {len(self.data['csv'])} rows")
            print(f"   Columns: {list(self.data['csv'].columns)}")

        # Load XLSX file if it exists
        xlsx_file = self.raw_path / "arduino_uno_raw.xlsx"
        if xlsx_file.exists():
            self.data["xlsx"] = pd.read_excel(xlsx_file)
            print(f"XLSX loaded: {len(self.data['xlsx'])} rows")
            print(f"   Columns: {list(self.data['xlsx'].columns)}")

    def clean_data(self):
        """Clean raw DataFrames: remove empty data, duplicates, and normalize columns."""
        print("\nCleaning data...")

        for key, df in self.data.items():
            # Drop rows where all values are NaN
            df = df.dropna(how="all")
            # Drop columns where all values are NaN
            df = df.dropna(axis=1, how="all")
            # Remove duplicate rows
            df = df.drop_duplicates()
            # Strip whitespace from string columns
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            # Normalize column names (lowercase + underscores)
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

            self.data[key] = df
            print(f"{key.upper()} cleaned: {len(df)} rows")

    def _extract_devices(self, df):
        """Extract device-level information for the Devices table."""
        print("  Extracting Devices...")

        device = {
            "DeviceID": 1,
            "DeviceName": "Arduino UNO R3",
            "DeviceType": "Microcontroller Board",
            "ImageURL": None,
            "CreatedAt": datetime.now().isoformat()
        }
        self.schema_mapping["Devices"].append(device)
        print(f"  Extracted {len(self.schema_mapping['Devices'])} devices")

    def _extract_components(self, df):
        """Extract common Arduino components and map them to the Components table."""
        print("  Extracting Components...")

        # Common Arduino-related components (description format: "Name - Description")
        common_components = {
            "digital_io": "Digital I/O Pins - General purpose digital input/output",
            "analog_input": "Analog Input Pins - Read analog sensors",
            "power": "5V Power Supply - Provides power to components",
            "gnd": "Ground - Common return path for circuits",
            "usb": "USB Port - For programming and power",
            "serial": "Serial Communication - For data transfer",
            "spi": "SPI Interface - Serial Peripheral Interface",
            "i2c": "I2C Interface - Two-wire communication",
            "led": "Built-in LED - Connected to digital pin 13",
            "button": "Reset Button - To reset the microcontroller"
        }

        component_id = 1
        for _, comp_desc in common_components.items():
            name_part = comp_desc.split(" - ")[0]
            desc_part = comp_desc.split(" - ")[1] if " - " in comp_desc else comp_desc

            component = {
                "ComponentID": component_id,
                "DeviceID": 1,
                "ComponentName": name_part,
                "Description": desc_part,
                "CreatedAt": datetime.now().isoformat()
            }
            self.schema_mapping["Components"].append(component)
            component_id += 1

        print(f"  Extracted {len(self.schema_mapping['Components'])} components")

    def _extract_guides(self, df):
        """Create high-level guides for the Guides table."""
        print("  Extracting Guides...")

        guides = [
            {
                "GuideID": 1,
                "DeviceID": 1,
                "Title": "Getting Started with Arduino UNO",
                "DateCreated": datetime.now().date().isoformat(),
                "GuideURL": "https://docs.arduino.cc/tutorials/uno-rev3/getting-started/",
                "CreatedAt": datetime.now().isoformat()
            },
            {
                "GuideID": 2,
                "DeviceID": 1,
                "Title": "Digital I/O Tutorial",
                "DateCreated": datetime.now().date().isoformat(),
                "GuideURL": None,
                "CreatedAt": datetime.now().isoformat()
            },
            {
                "GuideID": 3,
                "DeviceID": 1,
                "Title": "Analog Input and Sensors",
                "DateCreated": datetime.now().date().isoformat(),
                "GuideURL": None,
                "CreatedAt": datetime.now().isoformat()
            }
        ]

        self.schema_mapping["Guides"].extend(guides)
        print(f"  Extracted {len(self.schema_mapping['Guides'])} guides")

    def _extract_steps(self, df):
        """Create detailed step lists for each guide in the Steps table."""
        print("  Extracting Steps...")

        # Predefined steps for each guide
        steps_by_guide = {
            1: [
                "Connect the USB cable to your Arduino UNO board",
                "Download and install the Arduino IDE from arduino.cc",
                "Open the Arduino IDE and select your board type",
                "Select the correct COM port from Tools menu",
                "Load the Blink example from File > Examples > 01.Basics",
                "Click the Upload button to program your board",
                "Observe the LED blinking on the board"
            ],
            2: [
                "Understand digital pins (0-13) as INPUT or OUTPUT",
                "Use pinMode() to configure a pin",
                "Use digitalWrite() to set HIGH (5V) or LOW (0V)",
                "Use digitalRead() to read pin state",
                "Create a simple LED on/off circuit",
                "Test with a pushbutton as input",
                "Build a simple LED control with button"
            ],
            3: [
                "Connect an analog sensor to pin A0",
                "Use analogRead() to read the sensor value (0-1023)",
                "Map sensor values to useful ranges",
                "Use Serial.print() to view the values",
                "Open Serial Monitor to see data",
                "Create a light sensor application",
                "Calibrate sensors for accuracy"
            ]
        }

        step_id = 1
        for guide_id, steps in steps_by_guide.items():
            for step_num, description in enumerate(steps, start=1):
                step = {
                    "StepID": step_id,
                    "GuideID": guide_id,
                    "StepNumber": step_num,
                    "Description": description,
                    "CreatedAt": datetime.now().isoformat()
                }
                self.schema_mapping["Steps"].append(step)
                step_id += 1

        print(f"  Extracted {len(self.schema_mapping['Steps'])} steps")

    def map_to_schema(self):
        """Map cleaned data into schema-friendly structures (Devices, Components, Guides, Steps)."""
        print("\nMapping to database schema...")

        # Concatenate all cleaned DataFrames (if needed for future logic)
        all_data = pd.concat([df for df in self.data.values()], ignore_index=True)

        # Populate schema sections
        self._extract_devices(all_data)
        self._extract_components(all_data)
        self._extract_guides(all_data)
        self._extract_steps(all_data)

    def generate_sql_inserts(self):
        """Generate SQL INSERT statements for Devices, Components, Guides, and Steps."""
        print("\nGenerating SQL INSERT statements...")

        sql_statements = []

        # INSERT Devices
        sql_statements.append("-- ==================== DEVICES ====================\n")
        for device in self.schema_mapping["Devices"]:
            image_part = f"'{device['ImageURL']}'" if device["ImageURL"] else "NULL"
            sql = (
                "INSERT INTO Devices (DeviceName, DeviceType, ImageURL) \n"
                f"VALUES ('{device['DeviceName']}', '{device['DeviceType']}', {image_part});"
            )
            sql_statements.append(sql)

        # INSERT Components
        sql_statements.append("\n-- ==================== COMPONENTS ====================\n")
        for component in self.schema_mapping["Components"]:
            desc = component["Description"].replace("'", "''")
            sql = (
                "INSERT INTO Components (DeviceID, ComponentName, Description) \n"
                f"VALUES ({component['DeviceID']}, '{component['ComponentName']}', '{desc}');"
            )
            sql_statements.append(sql)

        # INSERT Guides
        sql_statements.append("\n-- ==================== GUIDES ====================\n")
        for guide in self.schema_mapping["Guides"]:
            url_part = f"'{guide['GuideURL']}'" if guide["GuideURL"] else "NULL"
            sql = (
                "INSERT INTO Guides (DeviceID, Title, DateCreated, GuideURL) \n"
                f"VALUES ({guide['DeviceID']}, '{guide['Title']}', '{guide['DateCreated']}', {url_part});"
            )
            sql_statements.append(sql)

        # INSERT Steps
        sql_statements.append("\n-- ==================== STEPS ====================\n")
        for step in self.schema_mapping["Steps"]:
            desc = step["Description"].replace("'", "''")
            sql = (
                "INSERT INTO Steps (GuideID, StepNumber, Description) \n"
                f"VALUES ({step['GuideID']}, {step['StepNumber']}, '{desc}');"
            )
            sql_statements.append(sql)

        return "\n".join(sql_statements)

    def save_results(self):
        """Save cleaned schema data, SQL statements, and a summary report as JSON files."""
        print("\nSaving results...")

        # 1. Save cleaned schema-mapped data as JSON
        cleaned_file = self.processed_path / "cleaned_data_enhanced.json"
        with open(cleaned_file, "w", encoding="utf-8") as f:
            json.dump(self.schema_mapping, f, indent=2, ensure_ascii=False)
        print(f"Saved cleaned data to: {cleaned_file}")

        # 2. Save generated SQL statements
        sql_statements = self.generate_sql_inserts()
        sql_file = self.output_path / "database_inserts_complete.sql"
        with open(sql_file, "w", encoding="utf-8") as f:
            f.write(sql_statements)
        print(f"Saved SQL inserts to: {sql_file}")

        # 3. Save a summary JSON with statistics and samples
        summary = {
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "devices": len(self.schema_mapping["Devices"]),
                "components": len(self.schema_mapping["Components"]),
                "guides": len(self.schema_mapping["Guides"]),
                "steps": len(self.schema_mapping["Steps"]),
                "total_records": sum(
                    [
                        len(self.schema_mapping["Devices"]),
                        len(self.schema_mapping["Components"]),
                        len(self.schema_mapping["Guides"]),
                        len(self.schema_mapping["Steps"]),
                    ]
                ),
            },
            "data_sample": {
                "device": self.schema_mapping["Devices"][0],
                "components_sample": self.schema_mapping["Components"][:3],
                "guides_sample": self.schema_mapping["Guides"][:2],
                "steps_sample": self.schema_mapping["Steps"][:3],
            },
        }

        summary_file = self.output_path / "data_cleaning_summary_enhanced.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Saved summary to: {summary_file}")

    def print_report(self):
        """Print a simple text report summarizing the cleaned and mapped data."""
        print("\n" + "=" * 70)
        print("ENHANCED DATA CLEANING REPORT")
        print("=" * 70)

        # Devices section
        print(f"\nDEVICES ({len(self.schema_mapping['Devices'])})")
        for device in self.schema_mapping["Devices"]:
            print(f"   • {device['DeviceName']} ({device['DeviceType']})")

        # Components section (show first 5)
        print(f"\nCOMPONENTS ({len(self.schema_mapping['Components'])})")
        for component in self.schema_mapping["Components"][:5]:
            print(f"   • {component['ComponentName']}")
        if len(self.schema_mapping["Components"]) > 5:
            print(f"   ... and {len(self.schema_mapping['Components']) - 5} more")

        # Guides section
        print(f"\nGUIDES ({len(self.schema_mapping['Guides'])})")
        for guide in self.schema_mapping["Guides"]:
            print(f"   • {guide['Title']}")

        # Steps section
        print(f"\nSTEPS ({len(self.schema_mapping['Steps'])})")
        print("   Total steps across all guides:")
        for guide in self.schema_mapping["Guides"]:
            guide_steps = [
                s for s in self.schema_mapping["Steps"] if s["GuideID"] == guide["GuideID"]
            ]
            print(f"   • Guide '{guide['Title']}': {len(guide_steps)} steps")

        print("\n" + "=" * 70)


def main():
    """Entry point to run the enhanced data cleaning and mapping pipeline."""
    print("=" * 70)
    print("SmartMentor: Enhanced Data Cleaning and Mapping")
    print("=" * 70)

    cleaner = EnhancedDataCleaner()
    cleaner.load_raw_data()
    cleaner.clean_data()
    cleaner.map_to_schema()
    cleaner.save_results()
    cleaner.print_report()

    print("\nEnhanced data cleaning complete.")


if __name__ == "__main__":
    main()
