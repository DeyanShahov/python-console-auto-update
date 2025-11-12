/**
 * Represents the result of checking for updates.
 */
export class UpdateCheckResult {
  /**
   * Creates a new UpdateCheckResult instance.
   * @param {Object} data - Result data
   * @param {boolean} data.hasUpdate - Whether an update is available
   * @param {VersionInfo} data.currentVersion - The current version
   * @param {VersionInfo} data.newVersion - The new version available
   * @param {string} data.releaseNotes - Release notes for the new version
   */
  constructor(data = {}) {
    this.hasUpdate = data.hasUpdate || false;
    this.currentVersion = data.currentVersion || null;
    this.newVersion = data.newVersion || null;
    this.releaseNotes = data.releaseNotes || null;
  }

  /**
   * Creates a result indicating no update is available.
   * @param {VersionInfo} currentVersion - The current version
   * @returns {UpdateCheckResult} Result with no update available
   */
  static noUpdate(currentVersion) {
    return new UpdateCheckResult({
      hasUpdate: false,
      currentVersion
    });
  }

  /**
   * Creates a result indicating an update is available.
   * @param {VersionInfo} currentVersion - The current version
   * @param {VersionInfo} newVersion - The new version available
   * @returns {UpdateCheckResult} Result with update available
   */
  static updateAvailable(currentVersion, newVersion) {
    return new UpdateCheckResult({
      hasUpdate: true,
      currentVersion,
      newVersion,
      releaseNotes: newVersion?.releaseNotes || null
    });
  }

  /**
   * Converts the result to JSON.
   * @returns {Object} JSON representation
   */
  toJSON() {
    return {
      hasUpdate: this.hasUpdate,
      currentVersion: this.currentVersion?.toJSON() || null,
      newVersion: this.newVersion?.toJSON() || null,
      releaseNotes: this.releaseNotes
    };
  }

  /**
   * Creates an UpdateCheckResult instance from JSON data.
   * @param {Object|string} json - JSON data or JSON string
   * @returns {UpdateCheckResult} New UpdateCheckResult instance
   */
  static fromJSON(json) {
    if (typeof json === 'string') {
      json = JSON.parse(json);
    }

    return new UpdateCheckResult({
      hasUpdate: json.hasUpdate,
      currentVersion: json.currentVersion ? VersionInfo.fromJSON(json.currentVersion) : null,
      newVersion: json.newVersion ? VersionInfo.fromJSON(json.newVersion) : null,
      releaseNotes: json.releaseNotes
    });
  }
}

// Import VersionInfo for the fromJSON method
import { VersionInfo } from './VersionInfo.js';
