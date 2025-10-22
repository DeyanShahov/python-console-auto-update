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

GITHUB_REPO = "https://github.com/DeyanShahov/python-console-auto-update.git"
APP_DIR = "python-console-app"

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
    print("🔄 Installing Python Console App...")
    print("📥 Downloading latest production version from GitHub...")

    # Step 1: Clone the production branch
    if os.path.exists(APP_DIR):
        print(f"⚠️  Directory '{APP_DIR}' already exists. Removing old installation...")
        shutil.rmtree(APP_DIR)

    clone_cmd = f"git clone --branch production --single-branch {GITHUB_REPO} {APP_DIR}"
    if not run_command(clone_cmd):
        print("❌ Failed to clone repository from GitHub")
        sys.exit(1)

    print("✅ Successfully downloaded the application")

    # Step 2: Change to app directory and check Python version
    os.chdir(APP_DIR)

    # Check Python version
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required")
        sys.exit(1)

    print("✅ Python version check passed")

    # Step 3: Make main.py executable on Unix systems
    if not os.name == 'nt':  # Not Windows
        try:
            os.chmod('main.py', 0o755)
        except OSError:
            pass  # Continue if chmod fails

    # Step 4: Clean up installation files (not needed for user)
    if os.path.exists('.git'):
        shutil.rmtree('.git')
    print("🧹 Cleaned up installation files")

    print("\n🎉 Installation completed successfully!")
    print(f"📂 Application installed in: {os.getcwd()}")
    print("\n🚀 To run the application:")
    print(f"   cd {APP_DIR}")
    print("   python main.py")

    # Step 5: Ask if user wants to run the app now
    try:
        choice = input("\n❓ Would you like to run the application now? (y/n): ").strip().lower()
        if choice == 'y':
            print("\n🏃 Starting Python Console App...\n")
            print("-" * 40)
            subprocess.run([sys.executable, 'main.py'])
        else:
            print("✅ Installation complete. You can run the app later with:")
            print(f"   cd {APP_DIR}")
            print("   python main.py")
    except KeyboardInterrupt:
        print("\n\n⏹️  Installation cancelled by user.")
        print("You can run the app later with:")
        print(f"   cd {APP_DIR}")
        print("   python main.py")

if __name__ == "__main__":
    main()
