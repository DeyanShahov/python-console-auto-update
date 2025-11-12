#!/usr/bin/env node

/**
 * CLI tool for checking and applying updates manually.
 * Usage: node check-updates.js [options]
 */

import { AutoUpdateService } from '../services/AutoUpdateService.js';
import { AutoUpdateConfig } from '../config/AutoUpdateConfig.js';
import logger from '../utils/logger.js';

/**
 * Parses command line arguments.
 * @returns {Object} Parsed arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    check: false,
    apply: false,
    config: null,
    verbose: false,
    help: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case '--check':
      case '-c':
        options.check = true;
        break;
      case '--apply':
      case '-a':
        options.apply = true;
        break;
      case '--config':
      case '-f':
        options.config = args[++i];
        break;
      case '--verbose':
      case '-v':
        options.verbose = true;
        break;
      case '--help':
      case '-h':
        options.help = true;
        break;
      default:
        if (arg.startsWith('--config=')) {
          options.config = arg.split('=')[1];
        } else {
          console.error(`Unknown option: ${arg}`);
          options.help = true;
        }
    }
  }

  // Default action is check
  if (!options.check && !options.apply && !options.help) {
    options.check = true;
  }

  return options;
}

/**
 * Prints help information.
 */
function printHelp() {
  console.log(`
AutoUpdate JS - Manual Update Tool

Usage: node check-updates.js [options]

Options:
  -c, --check          Check for available updates (default action)
  -a, --apply          Apply available updates
  -f, --config <file>  Path to configuration file (optional)
  -v, --verbose        Enable verbose logging
  -h, --help           Show this help message

Examples:
  node check-updates.js                    # Check for updates
  node check-updates.js --apply           # Check and apply updates
  node check-updates.js --config config.json --verbose

Configuration:
The tool looks for configuration in this order:
1. Configuration file specified with --config
2. Environment variables (AUTOUPDATE_*)
3. Default configuration

Environment Variables:
  AUTOUPDATE_GITHUB_OWNER          GitHub repository owner
  AUTOUPDATE_GITHUB_REPO           GitHub repository name
  AUTOUPDATE_PRODUCTION_BRANCH     Production branch (default: main)
  AUTOUPDATE_DEVELOPMENT_BRANCH    Development branch (default: main)
  AUTOUPDATE_USER_DATA_PATHS       Comma-separated user data paths
  AUTOUPDATE_VERSION_FILE_PATH     Path to version.json (default: version.json)
  AUTOUPDATE_BACKUP_DIRECTORY      Backup directory (default: backup/)
  AUTOUPDATE_HTTP_TIMEOUT          HTTP timeout in ms (default: 30000)
  AUTOUPDATE_ENABLE_LOGGING        Enable logging (default: true)
`);
}

/**
 * Loads configuration from various sources.
 * @param {string} configPath - Path to config file
 * @returns {Promise<AutoUpdateConfig>} Configuration instance
 */
async function loadConfig(configPath) {
  let config;

  if (configPath) {
    try {
      config = await AutoUpdateConfig.fromFile(configPath);
      console.log(`Loaded configuration from: ${configPath}`);
    } catch (error) {
      console.error(`Failed to load config file: ${error.message}`);
      process.exit(1);
    }
  } else {
    // Try environment variables first
    config = AutoUpdateConfig.fromEnvironment();

    // Validate if we have required fields
    const errors = config.validate();
    if (errors.length > 0) {
      console.log('Configuration loaded from environment variables');
      console.log('Validation errors:', errors.join(', '));
      console.log('Using default configuration...');
      config = new AutoUpdateConfig(); // Use defaults
    }
  }

  return config;
}

/**
 * Main CLI function.
 */
async function main() {
  const options = parseArgs();

  if (options.help) {
    printHelp();
    return;
  }

  // Configure logging
  logger.setLogLevel(options.verbose ? 'DEBUG' : 'INFO');

  try {
    // Load configuration
    const config = await loadConfig(options.config);

    // Validate configuration
    const errors = config.validate();
    if (errors.length > 0) {
      console.error('Configuration validation failed:');
      errors.forEach(error => console.error(`  - ${error}`));
      process.exit(1);
    }

    console.log(`🔍 Checking updates for: ${config.githubOwner}/${config.githubRepo}`);
    console.log(`📦 Production branch: ${config.productionBranch}`);

    // Create update service
    const updateService = new AutoUpdateService(config);

    if (options.check) {
      console.log('\n🔍 Checking for updates...');
      const result = await updateService.checkForUpdates();

      if (result.hasUpdate) {
        console.log('✅ Update available!');
        console.log(`   Current version: ${result.currentVersion?.version}`);
        console.log(`   New version: ${result.newVersion?.version}`);
        if (result.releaseNotes) {
          console.log(`   Release notes: ${result.releaseNotes}`);
        }

        if (!options.apply) {
          console.log('\n💡 Use --apply flag to install the update');
        }
      } else {
        console.log('✅ Your application is up to date');
        console.log(`   Current version: ${result.currentVersion?.version}`);
      }

      if (options.apply && result.hasUpdate) {
        console.log('\n⬇️ Applying update...');
        const updateResult = await updateService.applyUpdate();

        if (updateResult.isSuccess) {
          console.log('✅ Update applied successfully!');
          console.log(`   New version: ${updateResult.updatedVersion?.version}`);
        } else {
          console.error(`❌ Update failed: ${updateResult.errorMessage}`);
          process.exit(1);
        }
      }
    } else if (options.apply) {
      console.log('\n⬇️ Applying update...');
      const result = await updateService.applyUpdate();

      if (result.isSuccess) {
        console.log('✅ Update applied successfully!');
        console.log(`   New version: ${result.updatedVersion?.version}`);
      } else {
        console.error(`❌ Update failed: ${result.errorMessage}`);
        process.exit(1);
      }
    }

  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
    logger.error('CLI execution failed', error);
    process.exit(1);
  }
}

// Run CLI if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('Unhandled error:', error);
    process.exit(1);
  });
}

export { main as checkUpdates };
