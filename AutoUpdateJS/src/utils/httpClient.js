import https from 'https';
import http from 'http';

/**
 * Simple HTTP client for making requests to GitHub API.
 */
export class HttpClient {
  /**
   * Creates a new HttpClient instance.
   * @param {Object} options - Client options
   * @param {number} options.timeout - Request timeout in milliseconds
   * @param {Object} options.headers - Default headers
   */
  constructor(options = {}) {
    this.timeout = options.timeout || 30000;
    this.defaultHeaders = {
      'User-Agent': 'AutoUpdate-JS/1.0.0',
      'Accept': 'application/json',
      ...options.headers
    };
  }

  /**
   * Makes an HTTP GET request.
   * @param {string} url - The URL to request
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Response data
   */
  async get(url, options = {}) {
    return this.request('GET', url, null, options);
  }

  /**
   * Makes an HTTP request.
   * @param {string} method - HTTP method
   * @param {string} url - The URL to request
   * @param {string|null} data - Request body data
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Response data
   */
  async request(method, url, data = null, options = {}) {
    return new Promise((resolve, reject) => {
      const urlObj = new URL(url);
      const isHttps = urlObj.protocol === 'https:';

      const requestOptions = {
        hostname: urlObj.hostname,
        port: urlObj.port || (isHttps ? 443 : 80),
        path: urlObj.pathname + urlObj.search,
        method: method.toUpperCase(),
        headers: {
          ...this.defaultHeaders,
          ...options.headers
        },
        timeout: options.timeout || this.timeout
      };

      const client = isHttps ? https : http;
      const req = client.request(requestOptions, (res) => {
        let body = '';

        res.on('data', (chunk) => {
          body += chunk;
        });

        res.on('end', () => {
          try {
            let parsedBody;
            if (res.headers['content-type']?.includes('application/json')) {
              parsedBody = JSON.parse(body);
            } else {
              parsedBody = body;
            }

            resolve({
              statusCode: res.statusCode,
              headers: res.headers,
              body: parsedBody
            });
          } catch (error) {
            reject(new Error(`Failed to parse response: ${error.message}`));
          }
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });

      // Send request body if provided
      if (data) {
        req.write(data);
      }

      req.end();
    });
  }

  /**
   * Downloads a file from URL to a local path.
   * @param {string} url - The URL to download from
   * @param {string} localPath - Local file path to save to
   * @param {Object} options - Download options
   * @returns {Promise<void>}
   */
  async downloadFile(url, localPath, options = {}) {
    return new Promise((resolve, reject) => {
      const urlObj = new URL(url);
      const isHttps = urlObj.protocol === 'https:';

      const requestOptions = {
        hostname: urlObj.hostname,
        port: urlObj.port || (isHttps ? 443 : 80),
        path: urlObj.pathname + urlObj.search,
        method: 'GET',
        headers: {
          ...this.defaultHeaders,
          ...options.headers
        },
        timeout: options.timeout || this.timeout
      };

      const client = isHttps ? https : http;
      const req = client.request(requestOptions, (res) => {
        if (res.statusCode !== 200) {
          reject(new Error(`Download failed with status: ${res.statusCode}`));
          return;
        }

        const fs = require('fs');
        const fileStream = fs.createWriteStream(localPath);

        res.pipe(fileStream);

        fileStream.on('finish', () => {
          fileStream.close();
          resolve();
        });

        fileStream.on('error', (error) => {
          fs.unlink(localPath, () => {}); // Delete the file on error
          reject(error);
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Download timeout'));
      });

      req.end();
    });
  }
}

// Default instance
export const httpClient = new HttpClient();
