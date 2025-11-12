/**
 * AutoUpdate JS - Automatic update system for JavaScript/Node.js applications
 * @module AutoUpdateJS
 */

export { AutoUpdateService } from './src/services/AutoUpdateService.js';
export { VersionProvider } from './src/services/VersionProvider.js';
export { UpdateDownloader } from './src/services/UpdateDownloader.js';
export { UserDataManager } from './src/services/UserDataManager.js';

export { VersionInfo } from './src/models/VersionInfo.js';
export { UpdateResult } from './src/models/UpdateResult.js';
export { UpdateCheckResult } from './src/models/UpdateCheckResult.js';

export { AutoUpdateConfig } from './src/config/AutoUpdateConfig.js';

// Utility functions
export { default as logger } from './src/utils/logger.js';
export { httpClient } from './src/utils/httpClient.js';
export { fileUtils } from './src/utils/fileUtils.js';

// CLI tools
export { checkUpdates } from './src/cli/check-updates.js';

// Default configuration for AI-Online-Radio project
export const defaultConfig = {
  githubOwner: 'your-github-username',
  githubRepo: 'AI-Online-Radio',
  productionBranch: 'user-branch',
  developmentBranch: 'main-dev',
  userDataPaths: ['data/', 'uploads/', 'config/'],
  versionFilePath: 'version.json',
  backupDirectory: 'backup/',
  httpTimeout: 30000,
  enableLogging: true
};
