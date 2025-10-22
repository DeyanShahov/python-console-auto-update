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

# GitHub repository details (user will need to configure these)
GITHUB_REPO_OWNER = "your-username"  # Replace with actual GitHub username
GITHUB_REPO_NAME = "your-repo"       # Replace with actual repo name
GIT_BRANCH = "production"            # Branch for production releases

# Local version file
VERSION_FILE = "version.json"


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
    Returns tuple (version, commit_sha) or None if error.
    """
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/commits/{GIT_BRANCH}"
        with urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            commit_sha = data['sha']
            # For tag-based versioning, you would check tags instead
            return 'latest', commit_sha  # Simple versioning based on commits
    except (URLError, KeyError, json.JSONDecodeError) as e:
        print(f"Error checking for updates: {e}")
        return None


def backup_user_data():
    """
    Backup all JSON files (user data) before update.
    """
    backup_dir = f"backup_{int(datetime.now().timestamp())}"
    os.makedirs(backup_dir, exist_ok=True)

    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    for file in json_files:
        if file != VERSION_FILE:  # Don't backup version file
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"Backup: {file}")

    return backup_dir


def restore_user_data(backup_dir):
    """
    Restore JSON files after update.
    """
    if not os.path.exists(backup_dir):
        return

    for file in os.listdir(backup_dir):
        if file.endswith('.json'):
            src = os.path.join(backup_dir, file)
            dst = file
            shutil.copy2(src, dst)
            print(f"Restored: {file}")

    # Optionally remove backup after successful restore
    shutil.rmtree(backup_dir)
    print("Backup directory removed.")


def perform_update():
    """
    Perform git pull and update version file.
    """
    try:
        # Git pull
        result = subprocess.run(['git', 'pull', 'origin', GIT_BRANCH],
                              capture_output=True, text=True, cwd='.')

        if result.returncode == 0:
            print("Update successful.")

            # Update version file
            latest_version, commit_sha = get_latest_github_version() or ('updated', 'unknown')
            version_data = {
                'version': latest_version,
                'commit_sha': commit_sha,
                'last_updated': str(datetime.now())
            }

            with open(VERSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2)

            return True
        else:
            print(f"Update failed: {result.stderr}")
            return False

    except subprocess.SubprocessError as e:
        print(f"Error during update: {e}")
        return False


def check_for_updates():
    """
    Check for and apply updates if available.
    """
    print("Проверка за нови версии...")

    current_version, current_sha = get_current_version()
    latest_info = get_latest_github_version()

    if latest_info:
        latest_version, latest_sha = latest_info

        if latest_sha != current_sha:
            print(f"Намерена е нова версия: {latest_version}")
            print("Започваме обновяване...")

            # Backup user data
            backup_dir = backup_user_data()

            # Perform update
            if perform_update():
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
