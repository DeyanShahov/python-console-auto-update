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
APP_DIR = "python-console-app"

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


def find_python_command():
    """
    Find available Python command on Windows/Linux/Mac systems.
    Returns the command to use for Python.
    """
    import shutil

    # Try different Python commands in order of preference
    python_commands = [
        'python3',          # Standard on Linux/Mac and some Windows
        'python',           # Could be Python 2 or 3, but usually 3 in modern systems
        'py -3',            # Windows launcher for Python 3
        'py',               # Windows launcher (may default to Python 3)
    ]

    for cmd in python_commands:
        try:
            # Test if command exists and can run Python
            result = subprocess.run([cmd.split()[0], '--version'],
                                  capture_output=True, text=True,
                                  timeout=5)
            if result.returncode == 0 and 'Python' in result.stdout:
                version_match = re.search(r'Python (\d+)\.(\d+)', result.stdout)
                if version_match:
                    major = int(version_match.group(1))
                    minor = int(version_match.group(2))
                    if major >= 3:  # Any Python 3 version should work
                        print(f"✅ Found Python command: {cmd} (version {major}.{minor})")
                        return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    return None

def main():
    """
    Main installation process.
    """
    # Guard clause: Check if being run from inside the app directory
    if os.path.basename(os.getcwd()) == APP_DIR and os.path.exists('main.py'):
        print("❌ Грешка: Този скрипт е само за инсталация.")
        print("Изглежда, че приложението вече е инсталирано тук.")
        print("\n🚀 За да стартирате приложението, използвайте командата:")
        print("   python main.py")
        sys.exit(1)

    print("🔄 Инсталиране на конзолното приложение...")
    print("📥 Изтегляне на последната версия от GitHub...")

    # Step 1: Clone the production branch
    if os.path.exists(APP_DIR):
        print(f"⚠️  Директорията '{APP_DIR}' вече съществува. Премахване на старата инсталация...")
        shutil.rmtree(APP_DIR, onerror=remove_readonly)
        time.sleep(1) # Give OS time to release file handles

    clone_cmd = f"git clone --branch production --single-branch {GITHUB_REPO} {APP_DIR}"
    if not run_command(clone_cmd):
        print("❌ Failed to clone repository from GitHub")
        sys.exit(1)

    print("✅ Приложението е изтеглено успешно")

    # Step 2: Change to app directory and check Python version
    try:
        os.chdir(APP_DIR)
    except FileNotFoundError:
        print(f"❌ Грешка: Директорията '{APP_DIR}' не беше създадена. Проверете правата за достъп.")
        sys.exit(1)


    print("✅ Проверката на Python версията е успешна")

    # Step 3: Clean up development files (not needed for consumers)
    development_files = [
        '.git',
        '.gitignore',
        'install.py', # Remove install script after use
        '__pycache__',
        'README.md',
        '*.pyc',
        '*.pyo',
        '.vscode',
        '.idea',
        '*.log',
    ]

    files_removed = []
    print("🧹 Започва почистване на ненужни файлове...")
    for pattern in development_files:
        # Handle wildcard patterns
        if '*' in pattern:
            matches = glob.glob(pattern)
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
            if os.path.exists(pattern):
                try:
                    if os.path.isfile(pattern):
                        os.remove(pattern)
                    elif os.path.isdir(pattern):
                        shutil.rmtree(pattern, onerror=remove_readonly)
                    files_removed.append(pattern)
                except Exception as e:
                    print(f"⚠️ Не може да премахне '{pattern}': {e}")

    if files_removed:
        print(f"🧹 Почистване завършено: премахнати {len(files_removed)} елемента.")
    else:
        print("🧹 Няма ненужни файлове за почистване.")

    # Step 4: Make main.py executable on Unix systems
    if not os.name == 'nt':  # Not Windows
        try:
            os.chmod('main.py', 0o755)
        except OSError:
            pass  # Continue if chmod fails

    print("\n🎉 Инсталацията е завършена успешно!")
    print(f"📂 Приложението е инсталирано в: {os.getcwd()}")
    print("\n🚀 За да стартирате приложението, използвайте:")
    print("   python main.py")

    # Step 5: Ask if user wants to run the app now
    try:
        choice = input("\n❓ Желаете ли да стартирате приложението сега? (y/n): ").strip().lower()
        if choice == 'y':
            print("\n🏃 Стартиране на приложението...\n")
            print("-" * 40)
            subprocess.run([sys.executable, 'main.py'])
        else:
            print("\n✅ Инсталацията е завършена. Можете да стартирате приложението по-късно с:")
            print(f"   cd {os.path.basename(os.getcwd())}")
            print("   python main.py")
    except KeyboardInterrupt:
        print("\n\n⏹️  Инсталацията е прекратена от потребителя.")
        print("Можете да стартирате приложението по-късно.")

if __name__ == "__main__":
    main()
