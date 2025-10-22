#!/usr/bin/env python3
"""
Utility functions for JSON file management.
"""

import json
import os
import glob


def show_menu():
    """
    Display main menu and get user choice.
    """
    print("Изберете действие:")
    print("1. Четене от съществуващ JSON файл")
    print("2. Създаване на нов JSON файл")

    choice = input("Ваш избор (1 или 2): ").strip()
    return choice


def list_json_files():
    """
    List all JSON files in current directory.
    Returns list of .json files.
    """
    json_files = glob.glob("*.json")
    return json_files


def validate_file_choice(choice, files_list):
    """
    Validate user choice for file selection.
    Returns tuple (is_valid, file_path)
    """
    try:
        index = int(choice) - 1  # 0-based index
        if 0 <= index < len(files_list):
            return True, files_list[index]
        else:
            return False, None
    except ValueError:
        return False, None


def read_json_file():
    """
    Read and display content of a JSON file.
    """
    files = list_json_files()

    if not files:
        print("Няма JSON файлове в директорията.")
        return

    print("\nНалични JSON файлове:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

    choice = input("\nИзберете файл (номер): ").strip()

    is_valid, filepath = validate_file_choice(choice, files)
    if not is_valid:
        print("Невалиден избор.")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Extract content and meta-info
            content = data.get("content", "Няма съдържание.")
            meta_info = {k: v for k, v in data.items() if k != "content"}

            print(f"\nСъдържание на файла '{filepath}':")
            print(content)

            if meta_info:
                show_meta = input("\nЖелаете ли да видите мета информацията за файла? (y/n): ").strip().lower()
                if show_meta == 'y':
                    print("\nМета информация:")
                    print(json.dumps(meta_info, indent=2, ensure_ascii=False))
            
    except json.JSONDecodeError:
        print(f"Грешка: Файлът '{filepath}' не е валиден JSON.")
    except FileNotFoundError:
        print(f"Грешка: Файлът '{filepath}' не е намерен.")


def create_new_json():
    """
    Create a new JSON file.
    """
    filename = input("Въведете име на файла (без .json): ").strip()
    if not filename:
        print("Грешка: Името на файла не може да бъде празно.")
        return

    # Ensure .json extension
    if not filename.endswith('.json'):
        filename += '.json'

    # Check if file already exists
    if os.path.exists(filename):
        overwrite = input(f"Файлът '{filename}' вече съществува. Презаписване? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Операцията е отменена.")
            return

    content = input("Въведете съдържание на файла (текст/информация): ").strip()
    if not content:
        content = ""  # Allow empty content

    data = {
        "content": content,
        "created_at": str(os.environ.get('USERNAME', 'unknown')),
        "version": "1.0"
    }

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Файлът '{filename}' е създаден успешно.")
    except Exception as e:
        print(f"Грешка при запазването на файла: {e}")
