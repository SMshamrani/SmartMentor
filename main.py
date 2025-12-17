# main.py
# Entry point for the SmartMentor Phase 1 data pipeline.

from src.Phase1_OfflineProcessing.data_loader import DataLoader
# If you add a cleaner or mapper later, import them here as well.


def main():
    """Run the basic Phase 1 data pipeline: load raw data and convert it to JSON."""
    print("SmartMentor Phase 1 - Data Pipeline")

    # Initialize the data loader
    loader = DataLoader()

    # Load raw XLSX/CSV data and generate structured JSON
    data = loader.load_xlsx_csv()

    # TODO: Add data cleaning, mapping, and saving of additional outputs if needed
    print("Data loaded successfully")


if __name__ == "__main__":
    main()
