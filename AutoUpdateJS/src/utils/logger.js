/**
 * Simple logging utility for the AutoUpdate system.
 */

const LOG_LEVELS = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3
};

let currentLogLevel = LOG_LEVELS.INFO;
let enableLogging = true;

/**
 * Sets the current log level.
 * @param {string} level - Log level (ERROR, WARN, INFO, DEBUG)
 */
export function setLogLevel(level) {
  const upperLevel = level.toUpperCase();
  if (LOG_LEVELS[upperLevel] !== undefined) {
    currentLogLevel = LOG_LEVELS[upperLevel];
  }
}

/**
 * Enables or disables logging.
 * @param {boolean} enabled - Whether to enable logging
 */
export function setLoggingEnabled(enabled) {
  enableLogging = enabled;
}

/**
 * Logs an error message.
 * @param {string} message - Log message
 * @param {Error} error - Optional error object
 */
export function error(message, error = null) {
  if (!enableLogging || currentLogLevel < LOG_LEVELS.ERROR) return;

  const timestamp = new Date().toISOString();
  console.error(`[${timestamp}] ERROR: ${message}`);
  if (error) {
    console.error(error);
  }
}

/**
 * Logs a warning message.
 * @param {string} message - Log message
 */
export function warn(message) {
  if (!enableLogging || currentLogLevel < LOG_LEVELS.WARN) return;

  const timestamp = new Date().toISOString();
  console.warn(`[${timestamp}] WARN: ${message}`);
}

/**
 * Logs an info message.
 * @param {string} message - Log message
 */
export function info(message) {
  if (!enableLogging || currentLogLevel < LOG_LEVELS.INFO) return;

  const timestamp = new Date().toISOString();
  console.info(`[${timestamp}] INFO: ${message}`);
}

/**
 * Logs a debug message.
 * @param {string} message - Log message
 */
export function debug(message) {
  if (!enableLogging || currentLogLevel < LOG_LEVELS.DEBUG) return;

  const timestamp = new Date().toISOString();
  console.debug(`[${timestamp}] DEBUG: ${message}`);
}

// Default export with methods
export default {
  setLogLevel,
  setLoggingEnabled,
  error,
  warn,
  info,
  debug,
  LOG_LEVELS
};
