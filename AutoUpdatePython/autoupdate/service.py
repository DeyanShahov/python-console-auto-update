"""
Main AutoUpdate service that orchestrates the update process.
"""

import tempfile
import shutil
from typing import Optional
from .core import VersionInfo, UpdateCheckResult, UpdateResult
from .config import AutoUpdateConfig
from .version_provider import VersionProvider
from .downloader import UpdateDownloader
from .data_manager import UserDataManager


class AutoUpdateService:
    """
    Main service that orchestrates the auto-update process.
    """

    def __init__(self, config: AutoUpdateConfig):
        """
        Initialize AutoUpdateService.

        Args:
            config: AutoUpdateConfig instance
        """
        self.config = config
        self.version_provider = VersionProvider(config)
        self.update_downloader = UpdateDownloader(config)
        self.data_manager = UserDataManager(config)

    def check_for_updates(self) -> UpdateCheckResult:
        """
        Check for available updates.

        Returns:
            UpdateCheckResult instance
        """
        update_info = self.version_provider.check_for_update()

        if update_info['has_update']:
            return UpdateCheckResult.update_available(
                update_info['current_version'],
                update_info['remote_version']
            )
        else:
            return UpdateCheckResult.no_update(update_info['current_version'])

    def apply_update(self) -> UpdateResult:
        """
        Apply available updates.

        Returns:
            UpdateResult instance
        """
        try:
            # 1. Get remote version
            remote_version = self.version_provider.get_production_version()
            if remote_version is None:
                return UpdateResult.failure("Failed to fetch remote version information")

            # 2. Backup user data
            self.data_manager.backup_user_data()

            # 3. Download and apply update
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    extracted_path = self.update_downloader.download_and_extract(
                        self.config.github_owner,
                        self.config.github_repo,
                        self.config.production_branch,
                        temp_dir
                    )

                    # Apply files excluding user data and version file
                    exclude_paths = self.config.user_data_paths + [self.config.version_file_path]
                    self.update_downloader.apply_files(extracted_path, exclude_paths)

                except Exception as e:
                    # Restore user data on download/extract failure
                    self.data_manager.restore_user_data()
                    return UpdateResult.failure(f"Download/extract failed: {str(e)}")

            # 4. Update version file
            with open(self.config.version_file_path, 'w', encoding='utf-8') as f:
                f.write(remote_version.to_json())

            # 5. Restore user data
            self.data_manager.restore_user_data()

            return UpdateResult.success(remote_version)

        except Exception as e:
            # Ensure user data is restored on any error
            try:
                self.data_manager.restore_user_data()
            except Exception:
                pass  # Ignore restore errors during error handling

            return UpdateResult.failure(f"Update failed: {str(e)}")

    def check_and_apply_update(self):
        """
        Check for updates and apply them if available.

        Returns:
            Tuple of (UpdateCheckResult, UpdateResult or None)
        """
        check_result = self.check_for_updates()

        if not check_result.has_update:
            return check_result, None

        update_result = self.apply_update()
        return check_result, update_result

    def get_current_version(self) -> VersionInfo:
        """
        Get the current local version.

        Returns:
            VersionInfo instance
        """
        return self.version_provider.get_local_version()

    def get_latest_version(self) -> Optional[VersionInfo]:
        """
        Get the latest remote version.

        Returns:
            VersionInfo instance or None
        """
        return self.version_provider.get_production_version()

    def cleanup_backups(self, keep_count: int = 5) -> None:
        """
        Clean up old backup files.

        Args:
            keep_count: Number of backups to keep
        """
        self.data_manager.cleanup_old_backups(keep_count)

    def validate_config(self) -> list:
        """
        Validate the current configuration.

        Returns:
            List of validation error messages
        """
        return self.config.validate()
