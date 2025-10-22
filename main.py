#!/usr/bin/env python3
"""
Python Console App with Auto-Update from GitHub
Main entry point for the application.
"""

import os
import json
from utils import show_menu, read_json_file, create_new_json, DATA_DIR
from updater import check_for_updates


def get_app_version():
    """
    Get version and last updated date from version.json file.
    Returns tuple (version, last_updated) or defaults if file doesn't exist.
    """
    try:
        if os.path.exists("version.json"):
            with open("version.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                version = data.get('version', 'unknown')
                last_updated = data.get('last_updated', 'unknown')
                return version, last_updated
    except (json.JSONDecodeError, KeyError):
        pass
    return "development", "unknown"


def main():
    version, last_updated = get_app_version()
    print(f"=== Python Console App v{version} ({last_updated}) ===\n")

    # Ensure the data directory exists on startup
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Създадена директория за потребителски данни: '{DATA_DIR}'")

    # Check for updates on startup
    check_for_updates()

    while True:
        choice = show_menu()

        if choice == '1':
            # Read from existing JSON
            read_json_file()
        elif choice == '2':
            # Create new JSON
            create_new_json()
        else:
            print("Невалиден избор. Опитайте отново.")

        # Ask to continue or exit
        continue_app = input("\nЖелате ли да продължите? (y/n): ").strip().lower()
        if continue_app != 'y':
            print("Довиждане!")
            break


if __name__ == "__main__":
    main()
