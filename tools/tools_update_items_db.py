import os
import subprocess
import sqlite3
from src.database import db_manager
from src.item_manager import ItemManager

def main():
    from src.services.data_loader import DataLoader
    print("Starting DB Update via DataLoader...")
    try:
        success = DataLoader.load_initial_data()
        if success:
            print("Database updated successfully from JSON files.")
        else:
            print("Database update failed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
