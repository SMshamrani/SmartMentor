from src.Phase1_OfflineProcessing.data_loader import DataLoader
# من لو عندك cleaner / mapper تضيفها هنا

def main():
    print("SmartMentor Phase 1 - Data Pipeline")
    loader = DataLoader()
    data = loader.load_xlsx_csv()
    # TODO: نكمل: تنظيف + mapping + حفظ نتايج
    print("✅ Data loaded successfully")

if __name__ == "__main__":
    main()
