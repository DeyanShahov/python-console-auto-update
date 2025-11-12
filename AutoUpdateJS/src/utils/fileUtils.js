import fs from 'fs/promises';
import fsSync from 'fs';
import path from 'path';
import { createReadStream, createWriteStream } from 'fs';
import { pipeline } from 'stream/promises';

/**
 * File utilities for the AutoUpdate system.
 */

/**
 * Ensures a directory exists, creating it if necessary.
 * @param {string} dirPath - Directory path
 * @returns {Promise<void>}
 */
export async function ensureDirectory(dirPath) {
  try {
    await fs.mkdir(dirPath, { recursive: true });
  } catch (error) {
    if (error.code !== 'EEXIST') {
      throw error;
    }
  }
}

/**
 * Checks if a file exists.
 * @param {string} filePath - File path
 * @returns {Promise<boolean>} True if file exists
 */
export async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * Checks if a directory exists.
 * @param {string} dirPath - Directory path
 * @returns {Promise<boolean>} True if directory exists
 */
export async function directoryExists(dirPath) {
  try {
    const stats = await fs.stat(dirPath);
    return stats.isDirectory();
  } catch {
    return false;
  }
}

/**
 * Reads a JSON file and parses it.
 * @param {string} filePath - Path to JSON file
 * @returns {Promise<Object>} Parsed JSON data
 */
export async function readJsonFile(filePath) {
  const content = await fs.readFile(filePath, 'utf8');
  return JSON.parse(content);
}

/**
 * Writes data to a JSON file.
 * @param {string} filePath - Path to JSON file
 * @param {Object} data - Data to write
 * @param {number} indent - JSON indentation (default: 2)
 * @returns {Promise<void>}
 */
export async function writeJsonFile(filePath, data, indent = 2) {
  const json = JSON.stringify(data, null, indent);
  await fs.writeFile(filePath, json, 'utf8');
}

/**
 * Copies a file from source to destination.
 * @param {string} source - Source file path
 * @param {string} destination - Destination file path
 * @returns {Promise<void>}
 */
export async function copyFile(source, destination) {
  await ensureDirectory(path.dirname(destination));
  await fs.copyFile(source, destination);
}

/**
 * Copies a directory recursively.
 * @param {string} source - Source directory path
 * @param {string} destination - Destination directory path
 * @returns {Promise<void>}
 */
export async function copyDirectory(source, destination) {
  await ensureDirectory(destination);

  const entries = await fs.readdir(source, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(source, entry.name);
    const destPath = path.join(destination, entry.name);

    if (entry.isDirectory()) {
      await copyDirectory(srcPath, destPath);
    } else {
      await copyFile(srcPath, destPath);
    }
  }
}

/**
 * Removes a file or directory recursively.
 * @param {string} targetPath - Path to remove
 * @returns {Promise<void>}
 */
export async function remove(targetPath) {
  try {
    const stats = await fs.stat(targetPath);

    if (stats.isDirectory()) {
      await fs.rm(targetPath, { recursive: true, force: true });
    } else {
      await fs.unlink(targetPath);
    }
  } catch (error) {
    if (error.code !== 'ENOENT') {
      throw error;
    }
  }
}

/**
 * Gets all files in a directory recursively.
 * @param {string} dirPath - Directory path
 * @param {string[]} excludePatterns - Patterns to exclude
 * @returns {Promise<string[]>} Array of file paths
 */
export async function getAllFiles(dirPath, excludePatterns = []) {
  const files = [];

  async function scan(currentPath, relativePath = '') {
    const entries = await fs.readdir(currentPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(currentPath, entry.name);
      const relPath = path.join(relativePath, entry.name);

      // Check if path matches exclude patterns
      const shouldExclude = excludePatterns.some(pattern => {
        return relPath.includes(pattern) || entry.name.includes(pattern);
      });

      if (shouldExclude) {
        continue;
      }

      if (entry.isDirectory()) {
        await scan(fullPath, relPath);
      } else {
        files.push(fullPath);
      }
    }
  }

  await scan(dirPath);
  return files;
}

/**
 * Creates a temporary directory.
 * @param {string} prefix - Directory name prefix
 * @returns {Promise<string>} Path to temporary directory
 */
export async function createTempDirectory(prefix = 'autoupdate') {
  const tempDir = path.join(require('os').tmpdir(), `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  await ensureDirectory(tempDir);
  return tempDir;
}

/**
 * Extracts a ZIP file to a directory.
 * @param {string} zipPath - Path to ZIP file
 * @param {string} extractPath - Path to extract to
 * @returns {Promise<void>}
 */
export async function extractZip(zipPath, extractPath) {
  const yauzl = await import('yauzl');

  return new Promise((resolve, reject) => {
    yauzl.open(zipPath, { lazyEntries: true }, (error, zipfile) => {
      if (error) {
        reject(error);
        return;
      }

      zipfile.readEntry();

      zipfile.on('entry', async (entry) => {
        const entryPath = path.join(extractPath, entry.fileName);

        if (/\/$/.test(entry.fileName)) {
          // Directory entry
          await ensureDirectory(entryPath);
          zipfile.readEntry();
        } else {
          // File entry
          await ensureDirectory(path.dirname(entryPath));

          zipfile.openReadStream(entry, (error, readStream) => {
            if (error) {
              reject(error);
              return;
            }

            const writeStream = createWriteStream(entryPath);
            pipeline(readStream, writeStream)
              .then(() => zipfile.readEntry())
              .catch(reject);
          });
        }
      });

      zipfile.on('end', resolve);
      zipfile.on('error', reject);
    });
  });
}

// Default export with all utilities
export default {
  ensureDirectory,
  fileExists,
  directoryExists,
  readJsonFile,
  writeJsonFile,
  copyFile,
  copyDirectory,
  remove,
  getAllFiles,
  createTempDirectory,
  extractZip
};
