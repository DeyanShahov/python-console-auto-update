"""
Core classes for the AutoUpdate system.
"""

import json
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class VersionInfo:
    """
    Represents version information for the application.
    """
    version: str = "0.0.0"
    commit_sha: str = ""
    last_updated: str = ""
    release_notes: str = ""

    def __post_init__(self):
        """Ensure version is never None."""
        if self.version is None:
            self.version = "0.0.0"

    def compare_to(self, other: 'VersionInfo') -> int:
        """
        Compare this version with another version.

        Args:
            other: The other version to compare with

        Returns:
            1 if this version is greater, -1 if less, 0 if equal
        """
        if not other:
            return 1

        try:
            # Parse version strings like "1.2.3"
            this_parts = [int(x) for x in self.version.split('.')]
            other_parts = [int(x) for x in other.version.split('.')]

            # Pad shorter version with zeros
            max_len = max(len(this_parts), len(other_parts))
            this_parts.extend([0] * (max_len - len(this_parts)))
            other_parts.extend([0] * (max_len - len(other_parts)))

            for this_part, other_part in zip(this_parts, other_parts):
                if this_part > other_part:
                    return 1
                elif this_part < other_part:
                    return -1

            return 0
        except (ValueError, AttributeError):
            # Fallback to string comparison
            return (self.version > other.version) - (self.version < other.version)

    def is_greater_than(self, other: 'VersionInfo') -> bool:
        """Check if this version is greater than the other."""
        return self.compare_to(other) > 0

    def is_less_than(self, other: 'VersionInfo') -> bool:
        """Check if this version is less than the other."""
        return self.compare_to(other) < 0

    def equals(self, other: 'VersionInfo') -> bool:
        """Check if this version equals the other."""
        return self.compare_to(other) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "commit_sha": self.commit_sha,
            "last_updated": self.last_updated,
            "release_notes": self.release_notes
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VersionInfo':
        """Create from dictionary."""
        return cls(
            version=data.get("version", "0.0.0"),
            commit_sha=data.get("commit_sha", ""),
            last_updated=data.get("last_updated", ""),
            release_notes=data.get("release_notes", "")
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'VersionInfo':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class UpdateResult:
    """
    Represents the result of an update operation.
    """
    is_success: bool = False
    error_message: Optional[str] = None
    updated_version: Optional[VersionInfo] = None

    @classmethod
    def success(cls, updated_version: Optional[VersionInfo] = None) -> 'UpdateResult':
        """Create a successful update result."""
        return cls(is_success=True, updated_version=updated_version)

    @classmethod
    def failure(cls, error_message: str) -> 'UpdateResult':
        """Create a failed update result."""
        return cls(is_success=False, error_message=error_message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_success": self.is_success,
            "error_message": self.error_message,
            "updated_version": self.updated_version.to_dict() if self.updated_version else None
        }


@dataclass
class UpdateCheckResult:
    """
    Represents the result of checking for updates.
    """
    has_update: bool = False
    current_version: Optional[VersionInfo] = None
    new_version: Optional[VersionInfo] = None
    release_notes: Optional[str] = None

    @classmethod
    def no_update(cls, current_version: VersionInfo) -> 'UpdateCheckResult':
        """Create a result indicating no update is available."""
        return cls(has_update=False, current_version=current_version)

    @classmethod
    def update_available(cls, current_version: VersionInfo, new_version: VersionInfo) -> 'UpdateCheckResult':
        """Create a result indicating an update is available."""
        return cls(
            has_update=True,
            current_version=current_version,
            new_version=new_version,
            release_notes=new_version.release_notes if new_version else None
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "has_update": self.has_update,
            "current_version": self.current_version.to_dict() if self.current_version else None,
            "new_version": self.new_version.to_dict() if self.new_version else None,
            "release_notes": self.release_notes
        }
