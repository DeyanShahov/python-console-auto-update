using System.IO.Compression;
using AutoUpdate.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AutoUpdate.Services;

/// <summary>
/// Implementation of IUpdateDownloader for GitHub-based updates.
/// </summary>
public class UpdateDownloader : IUpdateDownloader
{
    private readonly AutoUpdateOptions _options;
    private readonly ILogger<UpdateDownloader> _logger;
    private readonly HttpClient _httpClient;

    public UpdateDownloader(
        IOptions<AutoUpdateOptions> options,
        ILogger<UpdateDownloader> logger,
        HttpClient httpClient)
    {
        _options = options.Value;
        _logger = logger;
        _httpClient = httpClient;
        _httpClient.Timeout = TimeSpan.FromSeconds(_options.HttpTimeoutSeconds);
    }

    /// <inheritdoc/>
    public async Task<string> DownloadAndExtractAsync(string owner, string repo, string branch, string tempPath, CancellationToken cancellationToken = default)
    {
        var zipUrl = $"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip";
        var zipPath = Path.Combine(tempPath, "update.zip");
        var extractPath = Path.Combine(tempPath, "extracted");

        try
        {
            _logger.LogInformation("Downloading update from: {Url}", zipUrl);

            // Ensure temp directory exists
            Directory.CreateDirectory(tempPath);

            // Download the ZIP file
            using (var response = await _httpClient.GetAsync(zipUrl, cancellationToken))
            {
                response.EnsureSuccessStatusCode();
                await using var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
                await using var fileStream = File.Create(zipPath);
                await stream.CopyToAsync(fileStream, cancellationToken);
            }

            _logger.LogInformation("Update downloaded successfully");

            // Extract the ZIP file
            _logger.LogInformation("Extracting update archive");
            ZipFile.ExtractToDirectory(zipPath, extractPath, true);

            // Find the extracted folder (GitHub ZIPs have format: repo-branch)
            var extractedDirs = Directory.GetDirectories(extractPath);
            if (extractedDirs.Length == 0)
            {
                throw new InvalidOperationException("No directories found in extracted archive");
            }

            var appPath = extractedDirs[0]; // Should be the only directory
            _logger.LogInformation("Update extracted to: {Path}", appPath);

            return appPath;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error downloading and extracting update");
            throw;
        }
        finally
        {
            // Clean up ZIP file
            if (File.Exists(zipPath))
            {
                File.Delete(zipPath);
            }
        }
    }

    /// <inheritdoc/>
    public async Task ApplyFilesAsync(string sourcePath, string[] excludePaths, CancellationToken cancellationToken = default)
    {
        var currentDir = Directory.GetCurrentDirectory();
        _logger.LogInformation("Applying update files from {Source} to {Target}", sourcePath, currentDir);

        // Convert exclude paths to full paths for comparison
        var excludeFullPaths = excludePaths
            .Select(p => Path.GetFullPath(p))
            .ToHashSet(StringComparer.OrdinalIgnoreCase);

        // Get all files and directories in source
        var allEntries = Directory.GetFileSystemEntries(sourcePath, "*", SearchOption.AllDirectories);

        foreach (var entry in allEntries)
        {
            cancellationToken.ThrowIfCancellationRequested();

            // Get relative path from source
            var relativePath = Path.GetRelativePath(sourcePath, entry);
            var targetPath = Path.Combine(currentDir, relativePath);

            // Skip excluded paths
            if (excludeFullPaths.Contains(Path.GetFullPath(targetPath)))
            {
                _logger.LogInformation("Skipping excluded path: {Path}", relativePath);
                continue;
            }

            if (File.Exists(entry))
            {
                // Ensure target directory exists
                var targetDir = Path.GetDirectoryName(targetPath);
                if (!string.IsNullOrEmpty(targetDir))
                {
                    Directory.CreateDirectory(targetDir);
                }

                // Copy file
                File.Copy(entry, targetPath, true);
                _logger.LogDebug("Updated file: {Path}", relativePath);
            }
            else if (Directory.Exists(entry))
            {
                // Create directory if it doesn't exist
                Directory.CreateDirectory(targetPath);
                _logger.LogDebug("Created directory: {Path}", relativePath);
            }
        }

        _logger.LogInformation("Update files applied successfully");
    }
}
