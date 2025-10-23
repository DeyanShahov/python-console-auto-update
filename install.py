#!/usr/bin/env python3
"""
Installation script for Python Console App
This script clones the production version from GitHub and sets up the application.
Usage: curl -sSL https://raw.githubusercontent.com/DeyanShahov/python-console-auto-update/production/install.py | python
"""

import subprocess
import sys
import os
import shutil
import re
import glob
import stat
import time

GITHUB_REPO = "https://github.com/DeyanShahov/python-console-auto-update.git"
APP_DIR = "python-console-app" # Default directory name for the installed app

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal on Windows."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"Error removing {path}: {e}")

def run_command(command, cwd=None):
    """
    Execute a shell command and return the result.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode != 0:
            print(f"Error executing: {command}")
            print(f"Output: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Failed to execute command: {command}")
        print(f"Error: {e}")
        return False

def main():
    """
    Main installation process.
    """
    # Determine the directory where the app will be installed
    install_target_dir = os.path.join(os.getcwd(), APP_DIR)

    # Guard clause: Check if being run from inside the app directory
    if os.path.exists(os.path.join(os.getcwd(), 'main.py')) and os.path.exists(os.path.join(os.getcwd(), 'updater.py')):
        print("❌ Грешка: Този скрипт е само за инсталация.")
        print("Изглежда, че приложението вече е инсталирано тук.")
        print("\n🚀 За да стартирате приложението, използвайте командата:")
        print("   python main.py")
        sys.exit(1)

    print("🔄 Инсталиране на конзолното приложение...")
    print("📥 Изтегляне на последната версия от GitHub...")

    # Step 1: Clone the production branch
    if os.path.exists(install_target_dir):
        print(f"⚠️  Директорията '{install_target_dir}' вече съществува. Премахване на старата инсталация...")
        shutil.rmtree(install_target_dir, onerror=remove_readonly)
        time.sleep(1) # Give OS time to release file handles

    clone_cmd = f"git clone --branch production --single-branch {GITHUB_REPO} {APP_DIR}"
    if not run_command(clone_cmd):
        print("❌ Failed to clone repository from GitHub")
        sys.exit(1)

    print("✅ Приложението е изтеглено успешно")

    # Step 2: Perform cleanup *before* changing directory
    # This ensures install.py is not trying to delete files it's running from
    print(f"🧹 Започва почистване на ненужни файлове в '{install_target_dir}'...")
    development_files = [
        '.git',
        '.gitignore',
        'install.py', # This install.py is the one *inside* the cloned repo, which should be removed
        'install.ps1', # This install.ps1 is also for installation, not needed after install
        '__pycache__',
        'README.md',
        'AUTO_UPDATE_WORKFLOW.md', # Development documentation, not needed for end users
        '.clinerules', # Development rules folder, not needed for end users
        '*.pyc',
        '*.pyo',
        '.vscode',
        '.idea',
        '*.log',
    ]

    files_removed = []
    for pattern in development_files:
        full_pattern_path = os.path.join(install_target_dir, pattern)
        if '*' in pattern:  # Handle wildcard patterns
            matches = glob.glob(full_pattern_path)
            for match in matches:
                if os.path.exists(match):
                    try:
                        if os.path.isfile(match):
                            os.remove(match)
                        elif os.path.isdir(match):
                            shutil.rmtree(match, onerror=remove_readonly)
                        files_removed.append(match)
                    except Exception as e:
                        print(f"⚠️ Не може да премахне '{match}': {e}")
        else: # Handle specific files/directories
            if os.path.exists(full_pattern_path):
                try:
                    if os.path.isfile(full_pattern_path):
                        os.remove(full_pattern_path)
                    elif os.path.isdir(full_pattern_path):
                        shutil.rmtree(full_pattern_path, onerror=remove_readonly)
                    files_removed.append(full_pattern_path)
                except Exception as e:
                    print(f"⚠️ Не може да премахне '{full_pattern_path}': {e}")

    if files_removed:
        print(f"🧹 Почистване завършено: премахнати {len(files_removed)} елемента.")
    else:
        print("🧹 Няма ненужни файлове за почистване.")

    # Step 3: Change to app directory and check Python version
    try:
        os.chdir(install_target_dir)
    except FileNotFoundError:
        print(f"❌ Грешка: Директорията '{install_target_dir}' не беше създадена. Проверете правата за достъп.")
        sys.exit(1)

    # Check Python version
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 или по-нова версия е необходима.")
        sys.exit(1)
    print("✅ Проверката на Python версията е успешна")

    # Step 4: Make main.py executable on Unix systems
    if not os.name == 'nt':  # Not Windows
        try:
            os.chmod('main.py', 0o755)
        except OSError:
            pass  # Continue if chmod fails

    print("\n🎉 Инсталацията е завършена успешно!")
    print(f"📂 Приложението е инсталирано в: {os.getcwd()}")
    # Step 5: Create start.bat for Windows users
    if os.name == 'nt': # Only for Windows
        start_bat_content = """@echo off
echo Starting Python Console App...
python main.py
pause"""
        start_bat_path = os.path.join(os.getcwd(), "start.bat")
        try:
            with open(start_bat_path, 'w', encoding='utf-8') as f:
                f.write(start_bat_content)
            print("✅ Създаден 'start.bat' файл за лесно стартиране.")
        except Exception as e:
            print(f"⚠️ Грешка при създаване на 'start.bat': {e}")

    print("\n🎉 Инсталацията е завършена успешно!")
    print(f"📂 Приложението е инсталирано в: {os.getcwd()}")
    print("\n🚀 За да стартирате приложението:")
    if os.name == 'nt':
        print("   Кликнете два пъти на 'start.bat' файла")
        print("   Или изпълнете: start.bat")
    else:
        print("   python main.py")

    # Step 6: Ask if user wants to run the app now
    try:
        choice = input("\n❓ Желаете ли да стартирате приложението сега? (y/n): ").strip().lower()
        if choice == 'y':
            print("\n🏃 Стартиране на приложението...\n")
            print("-" * 40)
            if os.name == 'nt':
                subprocess.run(['start.bat'], shell=True)
            else:
                subprocess.run([sys.executable, 'main.py'])
        else:
            print("\n✅ Инсталацията е завършена. Можете да стартирате приложението по-късно.")
    except KeyboardInterrupt:
        print("\n\n⏹️  Инсталацията е прекратена от потребителя.")
        print("Можете да стартирате приложението по-късно.")

if __name__ == "__main__":
    main()
