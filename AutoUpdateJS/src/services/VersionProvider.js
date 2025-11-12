import { VersionInfo } from '../models/VersionInfo.js';
import { httpClient } from '../utils/httpClient.js';
import { readJsonFile, fileExists } from '../utils/fileUtils.js';
import logger from '../utils/logger.js';

/**
 * Service for providing version information from local files and GitHub.
 */
export class VersionProvider {
  /**
   * Creates a new VersionProvider instance.
   * @param {AutoUpdateConfig} config - Configuration instance
   */
  constructor(config) {
    this.config = config;
    this.httpClient = new httpClient.constructor({
      timeout: config.httpTimeout
    });
  }

  /**
   * Gets the local version information.
   * @returns {Promise<VersionInfo>} Local version info
   */
  async getLocalVersion() {
    try {
      if (!(await fileExists(this.config.versionFilePath))) {
        logger.warn(`Version file not found at ${this.config.versionFilePath}, returning default version`);
        return new VersionInfo({ version: '0.0.0' });
      }

      const versionData = await readJsonFile(this.config.versionFilePath);
      const versionInfo = new VersionInfo(versionData);

      logger.info(`Local version loaded: ${versionInfo.version}`);
      return versionInfo;
    } catch (error) {
      logger.error(`Error reading local version file: ${error.message}`, error);
      return new VersionInfo({ version: '0.0.0' });
    }
  }

  /**
   * Gets the remote version information from GitHub.
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @param {string} branch - Branch name
   * @returns {Promise<VersionInfo|null>} Remote version info or null if error
   */
  async getRemoteVersion(owner, repo, branch) {
    try {
      const versionUrl = `${this.config.getRawContentUrl(branch)}/${this.config.versionFilePath}`;
      logger.info(`Fetching remote version from: ${versionUrl}`);

      const response = await this.httpClient.get(versionUrl);

      if (response.statusCode !== 200) {
        logger.warn(`Failed to fetch remote version: HTTP ${response.statusCode}`);
        return null;
      }

      const versionInfo = new VersionInfo(response.body);
      logger.info(`Remote version fetched: ${versionInfo.version}`);

      return versionInfo;
    } catch (error) {
      logger.error(`Error fetching remote version: ${error.message}`, error);
      return null;
    }
  }

  /**
   * Gets the remote version for the configured production branch.
   * @returns {Promise<VersionInfo|null>} Remote version info
   */
  async getProductionVersion() {
    return this.getRemoteVersion(
      this.config.githubOwner,
      this.config.githubRepo,
      this.config.productionBranch
    );
  }

  /**
   * Gets the remote version for the configured development branch.
   * @returns {Promise<VersionInfo|null>} Remote version info
   */
  async getDevelopmentVersion() {
    return this.getRemoteVersion(
      this.config.githubOwner,
      this.config.githubRepo,
      this.config.developmentBranch
    );
  }

  /**
   * Compares local and remote versions.
   * @param {VersionInfo} localVersion - Local version
   * @param {VersionInfo} remoteVersion - Remote version
   * @returns {number} 1 if remote is newer, -1 if local is newer, 0 if equal
   */
  compareVersions(localVersion, remoteVersion) {
    return remoteVersion.compareTo(localVersion);
  }

  /**
   * Checks if an update is available.
   * @returns {Promise<{hasUpdate: boolean, localVersion: VersionInfo, remoteVersion: VersionInfo|null}>}
   */
  async checkForUpdate() {
    const localVersion = await this.getLocalVersion();
    const remoteVersion = await this.getProductionVersion();

    if (!remoteVersion) {
      return {
        hasUpdate: false,
        localVersion,
        remoteVersion: null
      };
    }

    const hasUpdate = remoteVersion.isGreaterThan(localVersion);

    return {
      hasUpdate,
      localVersion,
      remoteVersion
    };
  }
}
