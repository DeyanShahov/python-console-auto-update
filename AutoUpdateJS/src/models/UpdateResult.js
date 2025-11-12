/**
 * Represents the result of an update operation.
 */
export class UpdateResult {
  /**
   * Creates a new UpdateResult instance.
   * @param {Object} data - Result data
   * @param {boolean} data.isSuccess - Whether the update was successful
   * @param {string} data.errorMessage - Error message if update failed
   * @param {VersionInfo} data.updatedVersion - The version that was updated to
   */
  constructor(data = {}) {
    this.isSuccess = data.isSuccess || false;
    this.errorMessage = data.errorMessage || null;
    this.updatedVersion = data.updatedVersion || null;
  }

  /**
   * Creates a successful update result.
   * @param {VersionInfo} updatedVersion - The version that was updated to
   * @returns {UpdateResult} Successful UpdateResult
   */
  static success(updatedVersion = null) {
    return new UpdateResult({
      isSuccess: true,
      updatedVersion
    });
  }

  /**
   * Creates a failed update result.
   * @param {string} errorMessage - The error message
   * @returns {UpdateResult} Failed UpdateResult
   */
  static failure(errorMessage) {
    return new UpdateResult({
      isSuccess: false,
      errorMessage
    });
  }

  /**
   * Converts the result to JSON.
   * @returns {Object} JSON representation
   */
  toJSON() {
    return {
      isSuccess: this.isSuccess,
      errorMessage: this.errorMessage,
      updatedVersion: this.updatedVersion?.toJSON() || null
    };
  }

  /**
   * Creates an UpdateResult instance from JSON data.
   * @param {Object|string} json - JSON data or JSON string
   * @returns {UpdateResult} New UpdateResult instance
   */
  static fromJSON(json) {
    if (typeof json === 'string') {
      json = JSON.parse(json);
    }

    return new UpdateResult({
      isSuccess: json.isSuccess,
      errorMessage: json.errorMessage,
      updatedVersion: json.updatedVersion ? VersionInfo.fromJSON(json.updatedVersion) : null
    });
  }
}

// Import VersionInfo for the fromJSON method
import { VersionInfo } from './VersionInfo.js';
