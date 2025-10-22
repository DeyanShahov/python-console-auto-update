#!/usr/bin/env python3
"""
Auto-update functionality for the application.
Checks for updates from GitHub and applies them safely.
"""

import json
import os
import shutil
import subprocess
from urllib.request import urlopen, URLError
from datetime import datetime
import zipfile
import stat
import time

# GitHub repository details (configured for this project)
GITHUB_REPO_OWNER = "DeyanShahov"    # GitHub username
GITHUB_REPO_NAME = "python-console-auto-update"  # Repository name
GIT_BRANCH = "production"            # Branch for production releases

# Local version file
VERSION_FILE = "version.json"

# Add a constant for the ZIP archive URL
GITHUB_ZIP_URL = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/archive/refs/heads/{GIT_BRANCH}.zip"

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal on Windows."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"Error removing {path}: {e}")

def get_current_version():
    """
    Get current version from version file or return default.
    """
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', '0.0.0'), data.get('commit_sha', '')
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return '0.0.0', ''


def get_latest_github_version():
    """
    Fetch latest version from GitHub API.
    Returns tuple (version, commit_sha, version_json_content) or None if error.
    """
    try:
        # Get latest commit SHA for the branch
        commit_url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/commits/{GIT_BRANCH}"
        with urlopen(commit_url) as response:
            commit_data = json.loads(response.read().decode('utf-8'))
            latest_commit_sha = commit_data['sha']

        # Get version.json content from GitHub
        version_json_url = f"https://raw.githubusercontent.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/{GIT_BRANCH}/version.json"
        with urlopen(version_json_url) as response:
            github_version_data = json.loads(response.read().decode('utf-8'))
            github_version = github_version_data.get('version', '0.0.0')

        return github_version, latest_commit_sha, github_version_data
    except (URLError, KeyError, json.JSONDecodeError) as e:
        print(f"Error checking for updates: {e}")
        return None


from utils import DATA_DIR # Import DATA_DIR

def backup_user_data():
    """
    Backup all JSON files (user data) from DATA_DIR before update.
    """
    backup_dir = f"backup_{int(datetime.now().timestamp())}"
    os.makedirs(backup_dir, exist_ok=True)

    if os.path.exists(DATA_DIR):
        json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
        for file in json_files:
            src_path = os.path.join(DATA_DIR, file)
            dst_path = os.path.join(backup_dir, file)
            shutil.copy2(src_path, dst_path)
            print(f"Backup: {src_path}")

    return backup_dir


def restore_user_data(backup_dir):
    """
    Restore JSON files to DATA_DIR after update.
    """
    if not os.path.exists(backup_dir):
        return

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    for file in os.listdir(backup_dir):
        if file.endswith('.json'):
            src = os.path.join(backup_dir, file)
            dst = os.path.join(DATA_DIR, file)
            shutil.copy2(src, dst)
            print(f"Restored: {dst}")

    # Optionally remove backup after successful restore
    shutil.rmtree(backup_dir, onerror=remove_readonly)
    print("Backup directory removed.")


def download_and_apply_update(github_version_data):
    """
    Downloads the latest production branch as a ZIP, extracts it,
    and applies the update, preserving user data.
    """
    print("Изтегляне на новата версия...")
    temp_zip_path = "update.zip"
    temp_extract_dir = "temp_update_extract"

    try:
        # Download the ZIP archive
        with urlopen(GITHUB_ZIP_URL) as response, open(temp_zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Архивът е изтеглен.")

        # Extract the archive
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)
        print("Архивът е разархивиран.")

        # The extracted folder will have a name like "repo-name-branch"
        extracted_folder_name = f"{GITHUB_REPO_NAME}-{GIT_BRANCH}"
        extracted_app_path = os.path.join(temp_extract_dir, extracted_folder_name)

        # Copy updated files, excluding the DATA_DIR and the version file itself
        for item_name in os.listdir(extracted_app_path):
            source_path = os.path.join(extracted_app_path, item_name)
            destination_path = os.path.join('.', item_name)

            # Skip the DATA_DIR and the version file
            if item_name == DATA_DIR or item_name == VERSION_FILE:
                print(f"Пропускане на директория/файл: {item_name}")
                continue
            
            # Overwrite existing files or copy new ones
            if os.path.isfile(source_path):
                shutil.copy2(source_path, destination_path)
            elif os.path.isdir(source_path):
                # For directories, remove existing and copy new
                if os.path.exists(destination_path):
                    shutil.rmtree(destination_path, onerror=remove_readonly)
                shutil.copytree(source_path, destination_path)
            print(f"Обновен файл/директория: {item_name}")

        # Update local version.json
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(github_version_data, f, indent=2)
        print("Локалният version.json е обновен.")

        return True
    except (URLError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as e:
        print(f"Грешка при изтегляне/прилагане на обновяването: {e}")
        return False
    finally:
        # Clean up temporary files
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir, onerror=remove_readonly)


def check_for_updates():
    """
    Check for and apply updates if available.
    """
    print("Проверка за нови версии...")

    current_version, _ = get_current_version() # current_sha is no longer relevant for comparison
    latest_info = get_latest_github_version()

    if latest_info:
        latest_github_version, _, github_version_data = latest_info

        # Compare versions (using the 'version' field from version.json)
        if latest_github_version != current_version:
            print(f"Намерена е нова версия: {latest_github_version} (текуща: {current_version})")
            print("Започваме обновяване...")

            # Backup user data
            backup_dir = backup_user_data()

            # Perform update
            if download_and_apply_update(github_version_data):
                # Restore user data
                restore_user_data(backup_dir)
                print("Обновяването е завършено успешно!")
            else:
                print("Грешка при обновяването. Възстановяване на данните...")
                restore_user_data(backup_dir)
                print("Обновяването е отменено.")
        else:
            print("Приложението е актуално.")
    else:
        print("Не може да се свърже с GitHub за проверка на обновления.")
