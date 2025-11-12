"""
Configuration system for AutoUpdate.
"""

import os
import json
from typing import List, Optional, Dict, Any


class AutoUpdateConfig:
    """
    Configuration class for AutoUpdate settings.
    """

    def __init__(self,
                 github_owner: str = "",
                 github_repo: str = "",
                 production_branch: str = "main",
                 development_branch: str = "main",
                 user_data_paths: Optional[List[str]] = None,
                 version_file_path: str = "version.json",
                 backup_directory: str = "backup/",
                 http_timeout: int = 30,
                 enable_logging: bool = True):
        """
        Initialize AutoUpdate configuration.

        Args:
            github_owner: GitHub repository owner
            github_repo: GitHub repository name
            production_branch: Branch for production updates
            development_branch: Branch for development (reference only)
            user_data_paths: Paths to user data directories to backup
            version_file_path: Path to version.json file
            backup_directory: Directory for backups
            http_timeout: HTTP request timeout in seconds
            enable_logging: Whether to enable logging
        """
        self.github_owner = github_owner
        self.github_repo = github_repo
        self.production_branch = production_branch
        self.development_branch = development_branch
        self.user_data_paths = user_data_paths or []
        self.version_file_path = version_file_path
        self.backup_directory = backup_directory
        self.http_timeout = http_timeout
        self.enable_logging = enable_logging

    @classmethod
    def from_environment(cls) -> 'AutoUpdateConfig':
        """
        Create configuration from environment variables.

        Environment variables:
        - AUTOUPDATE_GITHUB_OWNER
        - AUTOUPDATE_GITHUB_REPO
        - AUTOUPDATE_PRODUCTION_BRANCH (default: main)
        - AUTOUPDATE_DEVELOPMENT_BRANCH (default: main)
        - AUTOUPDATE_USER_DATA_PATHS (comma-separated)
        - AUTOUPDATE_VERSION_FILE_PATH (default: version.json)
        - AUTOUPDATE_BACKUP_DIRECTORY (default: backup/)
        - AUTOUPDATE_HTTP_TIMEOUT (default: 30)
        - AUTOUPDATE_ENABLE_LOGGING (default: true)
        """
        return cls(
            github_owner=os.getenv('AUTOUPDATE_GITHUB_OWNER', ''),
            github_repo=os.getenv('AUTOUPDATE_GITHUB_REPO', ''),
            production_branch=os.getenv('AUTOUPDATE_PRODUCTION_BRANCH', 'main'),
            development_branch=os.getenv('AUTOUPDATE_DEVELOPMENT_BRANCH', 'main'),
            user_data_paths=os.getenv('AUTOUPDATE_USER_DATA_PATHS', '').split(',') if os.getenv('AUTOUPDATE_USER_DATA_PATHS') else [],
            version_file_path=os.getenv('AUTOUPDATE_VERSION_FILE_PATH', 'version.json'),
            backup_directory=os.getenv('AUTOUPDATE_BACKUP_DIRECTORY', 'backup/'),
            http_timeout=int(os.getenv('AUTOUPDATE_HTTP_TIMEOUT', '30')),
            enable_logging=os.getenv('AUTOUPDATE_ENABLE_LOGGING', 'true').lower() == 'true'
        )

    @classmethod
    def from_file(cls, config_path: str) -> 'AutoUpdateConfig':
        """
        Create configuration from JSON file.

        Args:
            config_path: Path to JSON configuration file

        Returns:
            AutoUpdateConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return cls(
            github_owner=data.get('github_owner', ''),
            github_repo=data.get('github_repo', ''),
            production_branch=data.get('production_branch', 'main'),
            development_branch=data.get('development_branch', 'main'),
            user_data_paths=data.get('user_data_paths', []),
            version_file_path=data.get('version_file_path', 'version.json'),
            backup_directory=data.get('backup_directory', 'backup/'),
            http_timeout=data.get('http_timeout', 30),
            enable_logging=data.get('enable_logging', True)
        )

    def validate(self) -> List[str]:
        """
        Validate the configuration.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.github_owner:
            errors.append('github_owner is required')

        if not self.github_repo:
            errors.append('github_repo is required')

        if not self.production_branch:
            errors.append('production_branch is required')

        if self.http_timeout <= 0:
            errors.append('http_timeout must be greater than 0')

        return errors

    def get_github_api_base_url(self) -> str:
        """Get GitHub API base URL."""
        return 'https://api.github.com'

    def get_github_raw_base_url(self) -> str:
        """Get GitHub raw content base URL."""
        return 'https://raw.githubusercontent.com'

    def get_repository_api_url(self) -> str:
        """Get repository API URL."""
        return f"{self.get_github_api_base_url()}/repos/{self.github_owner}/{self.github_repo}"

    def get_raw_content_url(self, branch: Optional[str] = None) -> str:
        """Get raw content URL for repository."""
        target_branch = branch or self.production_branch
        return f"{self.get_github_raw_base_url()}/{self.github_owner}/{self.github_repo}/{target_branch}"

    def get_zip_download_url(self, branch: Optional[str] = None) -> str:
        """Get ZIP download URL for repository."""
        target_branch = branch or self.production_branch
        return f"https://github.com/{self.github_owner}/{self.github_repo}/archive/refs/heads/{target_branch}.zip"

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'github_owner': self.github_owner,
            'github_repo': self.github_repo,
            'production_branch': self.production_branch,
            'development_branch': self.development_branch,
            'user_data_paths': self.user_data_paths,
            'version_file_path': self.version_file_path,
            'backup_directory': self.backup_directory,
            'http_timeout': self.http_timeout,
            'enable_logging': self.enable_logging
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save_to_file(self, config_path: str) -> None:
        """Save configuration to JSON file."""
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutoUpdateConfig':
        """Create configuration from dictionary."""
        return cls(
            github_owner=data.get('github_owner', ''),
            github_repo=data.get('github_repo', ''),
            production_branch=data.get('production_branch', 'main'),
            development_branch=data.get('development_branch', 'main'),
            user_data_paths=data.get('user_data_paths', []),
            version_file_path=data.get('version_file_path', 'version.json'),
            backup_directory=data.get('backup_directory', 'backup/'),
            http_timeout=data.get('http_timeout', 30),
            enable_logging=data.get('enable_logging', True)
        )
