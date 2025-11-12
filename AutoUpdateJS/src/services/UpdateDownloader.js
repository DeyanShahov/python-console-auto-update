import path from 'path';
import { httpClient } from '../utils/httpClient.js';
import { createTempDirectory, extractZip, copyFile, ensureDirectory, remove, getAllFiles } from '../utils/fileUtils.js';
import logger from '../utils/logger.js';

/**
 * Service for downloading and applying updates from GitHub.
 */
export class UpdateDownloader {
  /**
   * Creates a new UpdateDownloader instance.
   * @param {AutoUpdateConfig} config - Configuration instance
   */
  constructor(config) {
    this.config = config;
    this.httpClient = new httpClient.constructor({
      timeout: config.httpTimeout
    });
  }

  /**
   * Downloads and extracts the update archive.
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @param {string} branch - Branch name
   * @param {string} tempPath - Temporary path for extraction
   * @returns {Promise<string>} Path to extracted application
   */
  async downloadAndExtract(owner, repo, branch, tempPath) {
    const zipUrl = `https://github.com/${owner}/${repo}/archive/refs/heads/${branch}.zip`;
    const zipPath = path.join(tempPath, 'update.zip');
    const extractPath = path.join(tempPath, 'extracted');

    try {
      logger.info(`Downloading update from: ${zipUrl}`);

      // Ensure temp directory exists
      await ensureDirectory(tempPath);

      // Download the ZIP file
      await this.httpClient.downloadFile(zipUrl, zipPath);
      logger.info('Update downloaded successfully');

      // Extract the ZIP file
      logger.info('Extracting update archive');
      await extractZip(zipPath, extractPath);

      // Find the extracted folder (GitHub ZIPs have format: repo-branch)
      const fs = await import('fs/promises');
      const entries = await fs.readdir(extractPath);
      const appFolder = entries.find(entry => entry.startsWith(`${repo}-`));

      if (!appFolder) {
        throw new Error('Could not find application folder in extracted archive');
      }

      const appPath = path.join(extractPath, appFolder);
      logger.info(`Update extracted to: ${appPath}`);

      return appPath;
    } catch (error) {
      logger.error(`Error downloading and extracting update: ${error.message}`, error);
      throw error;
    } finally {
      // Clean up ZIP file
      try {
        await remove(zipPath);
      } catch (error) {
        logger.debug(`Failed to clean up ZIP file: ${error.message}`);
      }
    }
  }

  /**
   * Applies the downloaded files to the application directory.
   * @param {string} sourcePath - Source path of extracted files
   * @param {string[]} excludePaths - Paths to exclude from copying
   * @returns {Promise<void>}
   */
  async applyFiles(sourcePath, excludePaths = []) {
    const currentDir = process.cwd();
    logger.info(`Applying update files from ${sourcePath} to ${currentDir}`);

    // Convert exclude paths to full paths for comparison
    const excludeFullPaths = excludePaths.map(p => path.resolve(p));

    // Get all files from source
    const allFiles = await getAllFiles(sourcePath);

    for (const sourceFile of allFiles) {
      // Get relative path from source
      const relativePath = path.relative(sourcePath, sourceFile);
      const targetPath = path.join(currentDir, relativePath);

      // Skip excluded paths
      if (excludeFullPaths.some(excludePath =>
        targetPath.startsWith(excludePath) || relativePath.startsWith(excludePath))) {
        logger.info(`Skipping excluded path: ${relativePath}`);
        continue;
      }

      try {
        await copyFile(sourceFile, targetPath);
        logger.debug(`Updated file: ${relativePath}`);
      } catch (error) {
        logger.warn(`Failed to update file ${relativePath}: ${error.message}`);
      }
    }

    logger.info('Update files applied successfully');
  }

  /**
   * Downloads and applies update for the configured repository.
   * @returns {Promise<string>} Path to extracted application
   */
  async downloadAndApplyUpdate() {
    const tempPath = await createTempDirectory('autoupdate');

    try {
      const extractedPath = await this.downloadAndExtract(
        this.config.githubOwner,
        this.config.githubRepo,
        this.config.productionBranch,
        tempPath
      );

      // Apply files excluding user data and version file
      const excludePaths = [
        ...this.config.userDataPaths,
        this.config.versionFilePath
      ];

      await this.applyFiles(extractedPath, excludePaths);

      return extractedPath;
    } finally {
      // Clean up temp directory
      try {
        await remove(tempPath);
        logger.debug('Temporary files cleaned up');
      } catch (error) {
        logger.debug(`Failed to clean up temp directory: ${error.message}`);
      }
    }
  }
}
