"""
User data manager for backup and restore operations.
"""

import os
import shutil
import time
from typing import List
from .config import AutoUpdateConfig


class UserDataManager:
    """
    Service for managing user data backup and restore operations.
    """

    def __init__(self, config: AutoUpdateConfig):
        """
        Initialize UserDataManager.

        Args:
            config: AutoUpdateConfig instance
        """
        self.config = config

    def backup(self, data_paths: List[str], backup_path: str) -> str:
        """
        Backup user data to a timestamped directory.

        Args:
            data_paths: List of paths to backup
            backup_path: Base backup directory path

        Returns:
            Path to the created backup directory
        """
        timestamp = int(time.time() * 1000)  # milliseconds
        full_backup_path = os.path.join(backup_path, f"backup_{timestamp}")

        os.makedirs(full_backup_path, exist_ok=True)

        for data_path in data_paths:
            if not os.path.exists(data_path):
                continue

            # Get the base name of the data path
            data_name = os.path.basename(data_path.rstrip(os.sep))
            backup_item_path = os.path.join(full_backup_path, data_name)

            try:
                if os.path.isdir(data_path):
                    # Copy directory recursively
                    shutil.copytree(data_path, backup_item_path, dirs_exist_ok=True)
                else:
                    # Copy single file
                    os.makedirs(os.path.dirname(backup_item_path), exist_ok=True)
                    shutil.copy2(data_path, backup_item_path)
            except Exception as e:
                # Log error but continue with other paths
                print(f"Warning: Failed to backup {data_path}: {e}")

        return full_backup_path

    def restore(self, backup_path: str, data_paths: List[str]) -> None:
        """
        Restore user data from the most recent backup.

        Args:
            backup_path: Base backup directory path
            data_paths: List of paths to restore
        """
        if not os.path.exists(backup_path):
            return

        # Find backup directories
        backup_dirs = [d for d in os.listdir(backup_path)
                      if os.path.isdir(os.path.join(backup_path, d)) and d.startswith('backup_')]

        if not backup_dirs:
            return

        # Sort by timestamp (newest first)
        backup_dirs.sort(key=lambda x: int(x.split('_')[1]), reverse=True)
        latest_backup = os.path.join(backup_path, backup_dirs[0])

        for data_path in data_paths:
            data_name = os.path.basename(data_path.rstrip(os.sep))
            backup_item_path = os.path.join(latest_backup, data_name)

            if not os.path.exists(backup_item_path):
                continue

            try:
                if os.path.isdir(backup_item_path):
                    # Remove existing directory if it exists
                    if os.path.exists(data_path):
                        shutil.rmtree(data_path)

                    # Restore directory
                    shutil.copytree(backup_item_path, data_path, dirs_exist_ok=True)
                else:
                    # Ensure target directory exists
                    os.makedirs(os.path.dirname(data_path), exist_ok=True)

                    # Restore file
                    shutil.copy2(backup_item_path, data_path)
            except Exception as e:
                # Log error but continue with other paths
                print(f"Warning: Failed to restore {data_path}: {e}")

        # Clean up the backup directory
        try:
            shutil.rmtree(latest_backup)
        except Exception as e:
            print(f"Warning: Failed to clean up backup directory: {e}")

    def backup_user_data(self) -> str:
        """
        Backup configured user data paths.

        Returns:
            Path to the backup directory
        """
        return self.backup(self.config.user_data_paths, self.config.backup_directory)

    def restore_user_data(self) -> None:
        """
        Restore configured user data paths.
        """
        self.restore(self.config.backup_directory, self.config.user_data_paths)

    def cleanup_old_backups(self, keep_count: int = 5) -> None:
        """
        Clean up old backup directories, keeping only the most recent ones.

        Args:
            keep_count: Number of recent backups to keep
        """
        if not os.path.exists(self.config.backup_directory):
            return

        backup_dirs = []
        for item in os.listdir(self.config.backup_directory):
            item_path = os.path.join(self.config.backup_directory, item)
            if os.path.isdir(item_path) and item.startswith('backup_'):
                try:
                    timestamp = int(item.split('_')[1])
                    backup_dirs.append((item_path, timestamp))
                except (ValueError, IndexError):
                    continue

        # Sort by timestamp (newest first)
        backup_dirs.sort(key=lambda x: x[1], reverse=True)

        # Remove old backups
        for backup_path, _ in backup_dirs[keep_count:]:
            try:
                shutil.rmtree(backup_path)
            except Exception as e:
                print(f"Warning: Failed to remove old backup {backup_path}: {e}")
