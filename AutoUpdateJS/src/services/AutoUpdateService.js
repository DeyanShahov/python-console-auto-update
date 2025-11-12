import { UpdateCheckResult } from '../models/UpdateCheckResult.js';
import { UpdateResult } from '../models/UpdateResult.js';
import { VersionProvider } from './VersionProvider.js';
import { UpdateDownloader } from './UpdateDownloader.js';
import { UserDataManager } from './UserDataManager.js';
import { writeJsonFile, createTempDirectory, remove } from '../utils/fileUtils.js';
import logger from '../utils/logger.js';

/**
 * Main service that orchestrates the auto-update process.
 */
export class AutoUpdateService {
  /**
   * Creates a new AutoUpdateService instance.
   * @param {AutoUpdateConfig} config - Configuration instance
   */
  constructor(config) {
    this.config = config;

    // Initialize services
    this.versionProvider = new VersionProvider(config);
    this.updateDownloader = new UpdateDownloader(config);
    this.userDataManager = new UserDataManager(config);

    // Configure logging
    logger.setLoggingEnabled(config.enableLogging);
  }

  /**
   * Checks for available updates.
   * @returns {Promise<UpdateCheckResult>} Update check result
   */
  async checkForUpdates() {
    try {
      logger.info(`Checking for updates from GitHub repository: ${this.config.githubOwner}/${this.config.githubRepo} branch: ${this.config.productionBranch}`);

      const updateInfo = await this.versionProvider.checkForUpdate();

      if (updateInfo.hasUpdate) {
        logger.info(`Update available: ${updateInfo.localVersion.version} -> ${updateInfo.remoteVersion.version}`);
        return UpdateCheckResult.updateAvailable(updateInfo.localVersion, updateInfo.remoteVersion);
      } else {
        logger.info(`Application is up to date: ${updateInfo.localVersion.version}`);
        return UpdateCheckResult.noUpdate(updateInfo.localVersion);
      }
    } catch (error) {
      logger.error(`Error checking for updates: ${error.message}`, error);

      // Return no update on error
      const localVersion = await this.versionProvider.getLocalVersion();
      return UpdateCheckResult.noUpdate(localVersion);
    }
  }

  /**
   * Applies available updates.
   * @returns {Promise<UpdateResult>} Update result
   */
  async applyUpdate() {
    let tempPath = null;

    try {
      logger.info('Starting update process');

      // 1. Get remote version info
      const remoteVersion = await this.versionProvider.getProductionVersion();
      if (!remoteVersion) {
        const errorMsg = 'Failed to fetch remote version information';
        logger.error(errorMsg);
        return UpdateResult.failure(errorMsg);
      }

      // 2. Backup user data
      logger.info('Backing up user data');
      await this.userDataManager.backupUserData();

      // 3. Create temp directory for update process
      tempPath = await createTempDirectory('autoupdate');

      // 4. Download and extract update
      logger.info('Downloading and extracting update');
      const extractedPath = await this.updateDownloader.downloadAndExtract(
        this.config.githubOwner,
        this.config.githubRepo,
        this.config.productionBranch,
        tempPath
      );

      // 5. Apply update files (exclude user data and version file)
      const excludePaths = [
        ...this.config.userDataPaths,
        this.config.versionFilePath
      ];

      logger.info('Applying update files');
      await this.updateDownloader.applyFiles(extractedPath, excludePaths);

      // 6. Update local version file
      logger.info(`Updating version file to: ${remoteVersion.version}`);
      await writeJsonFile(this.config.versionFilePath, remoteVersion.toJSON());

      // 7. Restore user data
      logger.info('Restoring user data');
      await this.userDataManager.restoreUserData();

      logger.info(`Update completed successfully: ${remoteVersion.version}`);
      return UpdateResult.success(remoteVersion);

    } catch (error) {
      logger.error(`Update failed: ${error.message}`, error);

      // Try to restore user data on failure
      try {
        logger.info('Attempting to restore user data after failed update');
        await this.userDataManager.restoreUserData();
      } catch (restoreError) {
        logger.error(`Failed to restore user data: ${restoreError.message}`, restoreError);
      }

      return UpdateResult.failure(`Update failed: ${error.message}`);
    } finally {
      // Clean up temporary files
      if (tempPath) {
        try {
          await remove(tempPath);
          logger.debug('Temporary files cleaned up');
        } catch (error) {
          logger.debug(`Failed to clean up temporary files: ${error.message}`);
        }
      }
    }
  }

  /**
   * Performs a complete update check and apply cycle.
   * @returns {Promise<{checkResult: UpdateCheckResult, updateResult: UpdateResult|null}>}
   */
  async checkAndApplyUpdate() {
    const checkResult = await this.checkForUpdates();

    if (!checkResult.hasUpdate) {
      return { checkResult, updateResult: null };
    }

    const updateResult = await this.applyUpdate();
    return { checkResult, updateResult };
  }

  /**
   * Gets the current local version.
   * @returns {Promise<VersionInfo>} Current version
   */
  async getCurrentVersion() {
    return this.versionProvider.getLocalVersion();
  }

  /**
   * Gets the latest remote version.
   * @returns {Promise<VersionInfo|null>} Latest remote version
   */
  async getLatestVersion() {
    return this.versionProvider.getProductionVersion();
  }

  /**
   * Cleans up old backup files.
   * @param {number} keepCount - Number of backups to keep
   * @returns {Promise<void>}
   */
  async cleanupBackups(keepCount = 5) {
    await this.userDataManager.cleanupOldBackups(keepCount);
  }

  /**
   * Validates the current configuration.
   * @returns {string[]} Array of validation errors (empty if valid)
   */
  validateConfig() {
    return this.config.validate();
  }
}
