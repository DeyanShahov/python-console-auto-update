/**
 * Represents version information for the application.
 */
export class VersionInfo {
  /**
   * Creates a new VersionInfo instance.
   * @param {Object} data - Version data
   * @param {string} data.version - Version string (e.g., "1.0.0")
   * @param {string} data.commit_sha - Commit SHA
   * @param {string} data.last_updated - Last updated date
   * @param {string} data.release_notes - Release notes
   */
  constructor(data = {}) {
    this.version = data.version || '0.0.0';
    this.commitSha = data.commit_sha || data.commitSha || '';
    this.lastUpdated = data.last_updated || data.lastUpdated || '';
    this.releaseNotes = data.release_notes || data.releaseNotes || '';
  }

  /**
   * Compares this version with another version.
   * @param {VersionInfo} other - The other version to compare with
   * @returns {number} 1 if this version is greater, -1 if less, 0 if equal
   */
  compareTo(other) {
    if (!other) return 1;

    try {
      const thisVersion = this.version.split('.').map(Number);
      const otherVersion = other.version.split('.').map(Number);

      for (let i = 0; i < Math.max(thisVersion.length, otherVersion.length); i++) {
        const thisPart = thisVersion[i] || 0;
        const otherPart = otherVersion[i] || 0;

        if (thisPart > otherPart) return 1;
        if (thisPart < otherPart) return -1;
      }

      return 0;
    } catch (error) {
      // Fallback to string comparison
      return this.version.localeCompare(other.version);
    }
  }

  /**
   * Determines if this version is greater than the specified version.
   * @param {VersionInfo} other - The version to compare with
   * @returns {boolean} True if this version is greater
   */
  isGreaterThan(other) {
    return this.compareTo(other) > 0;
  }

  /**
   * Determines if this version is less than the specified version.
   * @param {VersionInfo} other - The version to compare with
   * @returns {boolean} True if this version is less
   */
  isLessThan(other) {
    return this.compareTo(other) < 0;
  }

  /**
   * Determines if this version equals the specified version.
   * @param {VersionInfo} other - The version to compare with
   * @returns {boolean} True if versions are equal
   */
  equals(other) {
    return this.compareTo(other) === 0;
  }

  /**
   * Converts the version info to JSON.
   * @returns {Object} JSON representation
   */
  toJSON() {
    return {
      version: this.version,
      commit_sha: this.commitSha,
      last_updated: this.lastUpdated,
      release_notes: this.releaseNotes
    };
  }

  /**
   * Creates a VersionInfo instance from JSON data.
   * @param {Object|string} json - JSON data or JSON string
   * @returns {VersionInfo} New VersionInfo instance
   */
  static fromJSON(json) {
    if (typeof json === 'string') {
      json = JSON.parse(json);
    }
    return new VersionInfo(json);
  }
}
