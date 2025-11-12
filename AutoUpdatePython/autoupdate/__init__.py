"""
AutoUpdate Python - Automatic update system for Python applications from GitHub.

This package provides a complete solution for implementing automatic updates
in Python applications by checking for new versions from GitHub repositories.
"""

from .core import VersionInfo, UpdateResult, UpdateCheckResult
from .service import AutoUpdateService
from .version_provider import VersionProvider
from .downloader import UpdateDownloader
from .data_manager import UserDataManager
from .config import AutoUpdateConfig

__version__ = "1.0.0"
__author__ = "AutoUpdate System"
__description__ = "Automatic update system for Python applications from GitHub"

__all__ = [
    # Core classes
    "VersionInfo",
    "UpdateResult",
    "UpdateCheckResult",

    # Services
    "AutoUpdateService",
    "VersionProvider",
    "UpdateDownloader",
    "UserDataManager",

    # Configuration
    "AutoUpdateConfig",
]
