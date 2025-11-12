import path from 'path';
import { copyDirectory, ensureDirectory, remove, directoryExists } from '../utils/fileUtils.js';
import logger from '../utils/logger.js';

/**
 * Service for managing user data backup and restore operations.
 */
export class UserDataManager {
  /**
   * Creates a new UserDataManager instance.
   * @param {AutoUpdateConfig} config - Configuration instance
   */
  constructor(config) {
    this.config = config;
  }

  /**
   * Backs up user data to a timestamped directory.
   * @param {string[]} dataPaths - Paths to user data directories/files
   * @param {string} backupPath - Base backup directory path
   * @returns {Promise<string>} Path to the created backup directory
   */
  async backup(dataPaths, backupPath) {
    const timestamp = Date.now();
    const fullBackupPath = path.join(backupPath, `backup_${timestamp}`);

    try {
      logger.info(`Starting user data backup to: ${fullBackupPath}`);

      await ensureDirectory(fullBackupPath);

      for (const dataPath of dataPaths) {
        if (!(await directoryExists(dataPath))) {
          logger.warn(`Data path does not exist: ${dataPath}`);
          continue;
        }

        const dataName = path.basename(dataPath);
        const backupItemPath = path.join(fullBackupPath, dataName);

        try {
          await copyDirectory(dataPath, backupItemPath);
          logger.info(`Backed up directory: ${dataPath} -> ${backupItemPath}`);
        } catch (error) {
          logger.warn(`Failed to backup ${dataPath}: ${error.message}`);
        }
      }

      logger.info('User data backup completed successfully');
      return fullBackupPath;
    } catch (error) {
      logger.error(`Error during user data backup: ${error.message}`, error);
      throw error;
    }
  }

  /**
   * Restores user data from the most recent backup.
   * @param {string} backupPath - Base backup directory path
   * @param {string[]} dataPaths - Paths where to restore the data
   * @returns {Promise<void>}
   */
  async restore(backupPath, dataPaths) {
    try {
      logger.info(`Starting user data restore from: ${backupPath}`);

      // Find the most recent backup
      const fs = await import('fs/promises');
      let backupDirs = [];

      try {
        const entries = await fs.readdir(backupPath);
        backupDirs = entries
          .filter(entry => entry.startsWith('backup_'))
          .map(entry => path.join(backupPath, entry))
          .sort()
          .reverse(); // Most recent first
      } catch (error) {
        logger.warn(`No backup directory found at ${backupPath}`);
        return;
      }

      if (backupDirs.length === 0) {
        logger.warn('No backup directories found');
        return;
      }

      const latestBackup = backupDirs[0];
      logger.info(`Using latest backup: ${latestBackup}`);

      for (const dataPath of dataPaths) {
        const dataName = path.basename(dataPath);
        const backupItemPath = path.join(latestBackup, dataName);

        if (!(await directoryExists(backupItemPath))) {
          logger.warn(`Backup item does not exist: ${backupItemPath}`);
          continue;
        }

        try {
          // Remove existing directory if it exists
          if (await directoryExists(dataPath)) {
            await remove(dataPath);
          }

          // Restore from backup
          await copyDirectory(backupItemPath, dataPath);
          logger.info(`Restored directory: ${backupItemPath} -> ${dataPath}`);
        } catch (error) {
          logger.warn(`Failed to restore ${dataPath}: ${error.message}`);
        }
      }

      // Clean up backup directory
      try {
        await remove(latestBackup);
        logger.info(`Backup directory cleaned up: ${latestBackup}`);
      } catch (error) {
        logger.warn(`Failed to clean up backup directory: ${error.message}`);
      }

      logger.info('User data restore completed successfully');
    } catch (error) {
      logger.error(`Error during user data restore: ${error.message}`, error);
      throw error;
    }
  }

  /**
   * Backs up user data using the configured paths.
   * @returns {Promise<string>} Path to the created backup directory
   */
  async backupUserData() {
    return this.backup(this.config.userDataPaths, this.config.backupDirectory);
  }

  /**
   * Restores user data using the configured paths.
   * @returns {Promise<void>}
   */
  async restoreUserData() {
    return this.restore(this.config.backupDirectory, this.config.userDataPaths);
  }

  /**
   * Cleans up old backup directories, keeping only the most recent ones.
   * @param {number} keepCount - Number of recent backups to keep (default: 5)
   * @returns {Promise<void>}
   */
  async cleanupOldBackups(keepCount = 5) {
    try {
      const fs = await import('fs/promises');

      if (!(await directoryExists(this.config.backupDirectory))) {
        return;
      }

      const entries = await fs.readdir(this.config.backupDirectory);
      const backupDirs = entries
        .filter(entry => entry.startsWith('backup_'))
        .map(entry => ({
          name: entry,
          path: path.join(this.config.backupDirectory, entry),
          timestamp: parseInt(entry.replace('backup_', ''))
        }))
        .sort((a, b) => b.timestamp - a.timestamp); // Most recent first

      if (backupDirs.length <= keepCount) {
        return;
      }

      const dirsToRemove = backupDirs.slice(keepCount);

      for (const dir of dirsToRemove) {
        try {
          await remove(dir.path);
          logger.info(`Cleaned up old backup: ${dir.name}`);
        } catch (error) {
          logger.warn(`Failed to clean up backup ${dir.name}: ${error.message}`);
        }
      }

      logger.info(`Cleaned up ${dirsToRemove.length} old backup(s)`);
    } catch (error) {
      logger.error(`Error during backup cleanup: ${error.message}`, error);
    }
  }
}
