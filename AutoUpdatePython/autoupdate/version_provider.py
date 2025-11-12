"""
Version provider for GitHub-based version management.
"""

import json
import urllib.request
import urllib.error
from typing import Optional
from .core import VersionInfo
from .config import AutoUpdateConfig


class VersionProvider:
    """
    Service for providing version information from local files and GitHub.
    """

    def __init__(self, config: AutoUpdateConfig):
        """
        Initialize VersionProvider.

        Args:
            config: AutoUpdateConfig instance
        """
        self.config = config

    def get_local_version(self) -> VersionInfo:
        """
        Get the local version information from version.json file.

        Returns:
            VersionInfo instance
        """
        try:
            with open(self.config.version_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return VersionInfo.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # Return default version if file doesn't exist or is invalid
            return VersionInfo(version="0.0.0")

    def get_remote_version(self, owner: str, repo: str, branch: str) -> Optional[VersionInfo]:
        """
        Get remote version information from GitHub.

        Args:
            owner: GitHub repository owner
            repo: GitHub repository name
            branch: Branch name

        Returns:
            VersionInfo instance or None if error
        """
        try:
            version_url = f"{self.config.get_raw_content_url(branch)}/{self.config.version_file_path}"

            with urllib.request.urlopen(version_url, timeout=self.config.http_timeout) as response:
                if response.status != 200:
                    return None

                data = json.loads(response.read().decode('utf-8'))
                return VersionInfo.from_dict(data)

        except (urllib.error.URLError, json.JSONDecodeError, KeyError):
            return None

    def get_production_version(self) -> Optional[VersionInfo]:
        """
        Get the production version from GitHub.

        Returns:
            VersionInfo instance or None if error
        """
        return self.get_remote_version(
            self.config.github_owner,
            self.config.github_repo,
            self.config.production_branch
        )

    def get_development_version(self) -> Optional[VersionInfo]:
        """
        Get the development version from GitHub.

        Returns:
            VersionInfo instance or None if error
        """
        return self.get_remote_version(
            self.config.github_owner,
            self.config.github_repo,
            self.config.development_branch
        )

    def check_for_update(self) -> dict:
        """
        Check if an update is available.

        Returns:
            Dictionary with update information:
            {
                'has_update': bool,
                'current_version': VersionInfo,
                'remote_version': VersionInfo or None
            }
        """
        current_version = self.get_local_version()
        remote_version = self.get_production_version()

        if remote_version is None:
            return {
                'has_update': False,
                'current_version': current_version,
                'remote_version': None
            }

        has_update = remote_version.is_greater_than(current_version)

        return {
            'has_update': has_update,
            'current_version': current_version,
            'remote_version': remote_version
        }
