#!/usr/bin/env python3
"""
Python Console App with Auto-Update from GitHub
Main entry point for the application.
"""

import os
from utils import show_menu, read_json_file, create_new_json, DATA_DIR
from updater import check_for_updates


def main():
    print("=== Python Console App ===\n")

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
