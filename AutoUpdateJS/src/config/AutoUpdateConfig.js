/**
 * Configuration class for AutoUpdate settings.
 */
export class AutoUpdateConfig {
  /**
   * Creates a new AutoUpdateConfig instance.
   * @param {Object} options - Configuration options
   * @param {string} options.githubOwner - GitHub repository owner
   * @param {string} options.githubRepo - GitHub repository name
   * @param {string} options.productionBranch - Production branch for updates
   * @param {string} options.developmentBranch - Development branch (for reference)
   * @param {string[]} options.userDataPaths - Paths to backup during updates
   * @param {string} options.versionFilePath - Path to version.json file
   * @param {string} options.backupDirectory - Directory for backups
   * @param {number} options.httpTimeout - HTTP request timeout in milliseconds
   * @param {boolean} options.enableLogging - Whether to enable logging
   */
  constructor(options = {}) {
    this.githubOwner = options.githubOwner || '';
    this.githubRepo = options.githubRepo || '';
    this.productionBranch = options.productionBranch || 'main';
    this.developmentBranch = options.developmentBranch || 'main';
    this.userDataPaths = options.userDataPaths || [];
    this.versionFilePath = options.versionFilePath || 'version.json';
    this.backupDirectory = options.backupDirectory || 'backup/';
    this.httpTimeout = options.httpTimeout || 30000;
    this.enableLogging = options.enableLogging !== false;
  }

  /**
   * Creates a config instance from environment variables.
   * @returns {AutoUpdateConfig} Config instance
   */
  static fromEnvironment() {
    return new AutoUpdateConfig({
      githubOwner: process.env.AUTOUPDATE_GITHUB_OWNER,
      githubRepo: process.env.AUTOUPDATE_GITHUB_REPO,
      productionBranch: process.env.AUTOUPDATE_PRODUCTION_BRANCH || 'main',
      developmentBranch: process.env.AUTOUPDATE_DEVELOPMENT_BRANCH || 'main',
      userDataPaths: process.env.AUTOUPDATE_USER_DATA_PATHS ?
        process.env.AUTOUPDATE_USER_DATA_PATHS.split(',') : [],
      versionFilePath: process.env.AUTOUPDATE_VERSION_FILE_PATH || 'version.json',
      backupDirectory: process.env.AUTOUPDATE_BACKUP_DIRECTORY || 'backup/',
      httpTimeout: parseInt(process.env.AUTOUPDATE_HTTP_TIMEOUT) || 30000,
      enableLogging: process.env.AUTOUPDATE_ENABLE_LOGGING !== 'false'
    });
  }

  /**
   * Creates a config instance from a JSON file.
   * @param {string} configPath - Path to JSON config file
   * @returns {Promise<AutoUpdateConfig>} Config instance
   */
  static async fromFile(configPath) {
    try {
      const fs = await import('fs/promises');
      const content = await fs.readFile(configPath, 'utf8');
      const options = JSON.parse(content);
      return new AutoUpdateConfig(options);
    } catch (error) {
      throw new Error(`Failed to load config from file: ${error.message}`);
    }
  }

  /**
   * Validates the configuration.
   * @returns {string[]} Array of validation errors (empty if valid)
   */
  validate() {
    const errors = [];

    if (!this.githubOwner) {
      errors.push('githubOwner is required');
    }

    if (!this.githubRepo) {
      errors.push('githubRepo is required');
    }

    if (!this.productionBranch) {
      errors.push('productionBranch is required');
    }

    if (this.httpTimeout <= 0) {
      errors.push('httpTimeout must be greater than 0');
    }

    return errors;
  }

  /**
   * Gets the GitHub API base URL.
   * @returns {string} GitHub API base URL
   */
  getGitHubApiBaseUrl() {
    return 'https://api.github.com';
  }

  /**
   * Gets the GitHub raw content base URL.
   * @returns {string} GitHub raw content base URL
   */
  getGitHubRawBaseUrl() {
    return 'https://raw.githubusercontent.com';
  }

  /**
   * Gets the repository URL for API calls.
   * @returns {string} Repository API URL
   */
  getRepositoryApiUrl() {
    return `${this.getGitHubApiBaseUrl()}/repos/${this.githubOwner}/${this.githubRepo}`;
  }

  /**
   * Gets the raw content URL for the repository.
   * @param {string} branch - Branch name (defaults to production branch)
   * @returns {string} Raw content URL
   */
  getRawContentUrl(branch = null) {
    const targetBranch = branch || this.productionBranch;
    return `${this.getGitHubRawBaseUrl()}/${this.githubOwner}/${this.githubRepo}/${targetBranch}`;
  }

  /**
   * Gets the ZIP download URL for the repository.
   * @param {string} branch - Branch name (defaults to production branch)
   * @returns {string} ZIP download URL
   */
  getZipDownloadUrl(branch = null) {
    const targetBranch = branch || this.productionBranch;
    return `https://github.com/${this.githubOwner}/${this.githubRepo}/archive/refs/heads/${targetBranch}.zip`;
  }

  /**
   * Converts the config to a plain object.
   * @returns {Object} Plain object representation
   */
  toJSON() {
    return {
      githubOwner: this.githubOwner,
      githubRepo: this.githubRepo,
      productionBranch: this.productionBranch,
      developmentBranch: this.developmentBranch,
      userDataPaths: this.userDataPaths,
      versionFilePath: this.versionFilePath,
      backupDirectory: this.backupDirectory,
      httpTimeout: this.httpTimeout,
      enableLogging: this.enableLogging
    };
  }

  /**
   * Creates a config instance from a plain object.
   * @param {Object} obj - Plain object
   * @returns {AutoUpdateConfig} Config instance
   */
  static fromJSON(obj) {
    return new AutoUpdateConfig(obj);
  }
}
