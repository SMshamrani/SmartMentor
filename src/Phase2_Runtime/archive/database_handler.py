# src/database_handler.py

import json
import os

import psycopg2
from psycopg2.extras import execute_batch  # Reserved for future batch inserts
from config import Config


class DatabaseHandler:
    """Handle PostgreSQL connection, schema creation, and data insertion."""

    def __init__(self):
        # Connection and cursor will be created on demand
        self.conn = None
        self.cursor = None

    def connect(
        self,
        dbname="arduino_db",
        user="postgres",
        password="password",
        host="localhost",
        port="5432",
    ):
        """Connect to the PostgreSQL database using the provided credentials."""
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port,
            )
            self.cursor = self.conn.cursor()
            print("Connected to database successfully")
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    def create_tables(self):
        """Create database tables from the schema.sql file."""
        try:
            schema_path = os.path.join("database", "schema.sql")
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()

            # Execute full schema (may contain multiple statements)
            self.cursor.execute(schema_sql)
            self.conn.commit()
            print("Tables created successfully")
            return True
        except Exception as e:
            print(f"Error creating tables: {e}")
            if self.conn:
                self.conn.rollback()
            return False

    def insert_scraped_data(self, json_file_path):
        """Insert scraper JSON data into Devices, Components, and Guides tables."""
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Track already added device names to avoid duplicates
            devices_added = set()

            for item in data:
                device_name = item.get("component", "Unknown")

                # Check if device already exists in the database
                self.cursor.execute(
                    "SELECT DeviceID FROM Devices WHERE DeviceName = %s",
                    (device_name,),
                )
                existing = self.cursor.fetchone()

                if not existing and device_name not in devices_added:
                    # Insert new device
                    self.cursor.execute(
                        """
                        INSERT INTO Devices (DeviceName, DeviceType, ImageURL) 
                        VALUES (%s, %s, %s)
                        RETURNING DeviceID
                        """,
                        (
                            device_name,
                            item.get("type", "board"),
                            item.get("image", ""),
                        ),
                    )
                    device_id = self.cursor.fetchone()[0]
                    devices_added.add(device_name)
                    print(f"  Added device: {device_name}")
                elif existing:
                    device_id = existing[0]
                else:
                    # Fallback in case of unexpected state
                    continue

                # Insert into Components table if the item is a component
                if item.get("type") == "component":
                    self.cursor.execute(
                        """
                        INSERT INTO Components (DeviceID, ComponentName, Description)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            device_id,
                            device_name,
                            item.get("description", ""),
                        ),
                    )

                # Insert a guide entry related to this device
                self.cursor.execute(
                    """
                    INSERT INTO Guides (DeviceID, Title, DateCreated, GuideURL)
                    VALUES (%s, %s, CURRENT_DATE, %s)
                    """,
                    (
                        device_id,
                        f"Guide for {device_name}",
                        item.get("link", ""),
                    ),
                )

            self.conn.commit()
            print(f"Inserted {len(data)} scraped items into database")
            return True

        except Exception as e:
            print(f"Error inserting scraped data: {e}")
            if self.conn:
                self.conn.rollback()
            return False

    def insert_llm_classified_data(self, json_file_path):
        """Insert LLM-classified guide data into the Guides table."""
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data:
                original = item.get("original", {})
                category = item.get("category", "Unknown")
                title = original.get("title", "Untitled")
                snippet = original.get("snippet", "")

                # Insert as a guide not directly tied to a specific DeviceID (DeviceID NULL)
                self.cursor.execute(
                    """
                    INSERT INTO Guides (DeviceID, Title, DateCreated, GuideURL)
                    VALUES (NULL, %s, CURRENT_DATE, %s)
                    """,
                    (
                        f"{title} [Category: {category}]",
                        original.get("link", ""),
                    ),
                )

            self.conn.commit()
            print(f"Inserted {len(data)} LLM-classified items")
            return True

        except Exception as e:
            print(f"Error inserting LLM-classified data: {e}")
            if self.conn:
                self.conn.rollback()
            return False

    def compare_data_counts(self):
        """Compare counts of devices, guides, and components for basic statistics."""
        try:
            queries = {
                "scraper_devices": "SELECT COUNT(*) FROM Devices",
                "scraper_guides": "SELECT COUNT(*) FROM Guides WHERE DeviceID IS NOT NULL",
                "llm_guides": "SELECT COUNT(*) FROM Guides WHERE DeviceID IS NULL",
                "total_components": "SELECT COUNT(*) FROM Components",
            }

            results = {}
            for name, query in queries.items():
                self.cursor.execute(query)
                count = self.cursor.fetchone()[0]
                results[name] = count

            print("\nDatabase Statistics:")
            print("-" * 30)
            for name, count in results.items():
                print(f"{name.replace('_', ' ').title()}: {count}")
            print("-" * 30)

            return results

        except Exception as e:
            print(f"Error counting data: {e}")
            return {}

    def close(self):
        """Close the database cursor and connection cleanly."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed")


def test_database_connection():
    """Helper function to test database connection and basic pipeline."""
    db = DatabaseHandler()

    # You can replace these with values from Config or environment variables if needed
    if db.connect(
        dbname="arduino_db",
        user="postgres",
        password="password",
        host="localhost",
        port="5432",
    ):
        # 1. Create tables (safe to call if schema guards exist)
        db.create_tables()

        # 2. Insert scraper JSON data if file exists
        scraper_file = "data/scraped_json/comprehensive_arduino_data.json"
        if os.path.exists(scraper_file):
            db.insert_scraped_data(scraper_file)
        else:
            print(f"Scraper file not found: {scraper_file}")

        # 3. Insert LLM-classified data if file exists
        llm_file = "data/processed/llm_classified.json"
        if os.path.exists(llm_file):
            db.insert_llm_classified_data(llm_file)
        else:
            print(f"LLM file not found: {llm_file}")

        # 4. Print simple statistics summary
        db.compare_data_counts()

        # 5. Close the connection
        db.close()


if __name__ == "__main__":
    test_database_connection()
