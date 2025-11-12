"""
Update downloader for GitHub-based updates.
"""

import os
import shutil
import tempfile
import urllib.request
import urllib.error
import zipfile
from pathlib import Path
from typing import List
from .config import AutoUpdateConfig


class UpdateDownloader:
    """
    Service for downloading and applying updates from GitHub.
    """

    def __init__(self, config: AutoUpdateConfig):
        """
        Initialize UpdateDownloader.

        Args:
            config: AutoUpdateConfig instance
        """
        self.config = config

    def download_and_extract(self, owner: str, repo: str, branch: str, temp_path: str) -> str:
        """
        Download and extract update archive.

        Args:
            owner: GitHub repository owner
            repo: GitHub repository name
            branch: Branch name
            temp_path: Temporary path for extraction

        Returns:
            Path to extracted application directory

        Raises:
            Exception: If download or extraction fails
        """
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        zip_path = os.path.join(temp_path, "update.zip")
        extract_path = os.path.join(temp_path, "extracted")

        try:
            # Ensure temp directory exists
            os.makedirs(temp_path, exist_ok=True)

            # Download ZIP file
            with urllib.request.urlopen(zip_url, timeout=self.config.http_timeout) as response:
                if response.status != 200:
                    raise Exception(f"Download failed with status: {response.status}")

                with open(zip_path, 'wb') as f:
                    shutil.copyfileobj(response, f)

            # Extract ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # Find the extracted application directory
            # GitHub ZIPs have format: repo-branch
            extracted_dirs = [d for d in os.listdir(extract_path)
                            if os.path.isdir(os.path.join(extract_path, d))]

            if not extracted_dirs:
                raise Exception("No directories found in extracted archive")

            app_dir = extracted_dirs[0]  # Should be the only directory
            app_path = os.path.join(extract_path, app_dir)

            return app_path

        except Exception as e:
            raise Exception(f"Download and extract failed: {str(e)}")
        finally:
            # Clean up ZIP file
            if os.path.exists(zip_path):
                os.unlink(zip_path)

    def apply_files(self, source_path: str, exclude_paths: List[str]) -> None:
        """
        Apply downloaded files to the application directory.

        Args:
            source_path: Path to extracted application files
            exclude_paths: Paths to exclude from copying
        """
        current_dir = os.getcwd()

        # Convert exclude paths to absolute paths for comparison
        exclude_abs_paths = [os.path.abspath(p) for p in exclude_paths]

        # Walk through all files in source
        for root, dirs, files in os.walk(source_path):
            # Calculate relative path from source
            rel_root = os.path.relpath(root, source_path)

            for file in files:
                source_file = os.path.join(root, file)

                if rel_root == ".":
                    target_file = os.path.join(current_dir, file)
                else:
                    target_file = os.path.join(current_dir, rel_root, file)

                # Skip excluded paths
                target_abs = os.path.abspath(target_file)
                if any(target_abs.startswith(excl) for excl in exclude_abs_paths):
                    continue

                # Ensure target directory exists
                os.makedirs(os.path.dirname(target_file), exist_ok=True)

                # Copy file
                shutil.copy2(source_file, target_file)

    def download_and_apply_update(self) -> str:
        """
        Download and apply update for the configured repository.

        Returns:
            Path to extracted application directory
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            extracted_path = self.download_and_extract(
                self.config.github_owner,
                self.config.github_repo,
                self.config.production_branch,
                temp_dir
            )

            # Apply files excluding user data and version file
            exclude_paths = self.config.user_data_paths + [self.config.version_file_path]
            self.apply_files(extracted_path, exclude_paths)

            return extracted_path
