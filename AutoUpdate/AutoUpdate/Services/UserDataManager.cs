using AutoUpdate.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AutoUpdate.Services;

/// <summary>
/// Implementation of IUserDataManager for backing up and restoring user data.
/// </summary>
public class UserDataManager : IUserDataManager
{
    private readonly AutoUpdateOptions _options;
    private readonly ILogger<UserDataManager> _logger;

    public UserDataManager(
        IOptions<AutoUpdateOptions> options,
        ILogger<UserDataManager> logger)
    {
        _options = options.Value;
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task BackupAsync(string[] dataPaths, string backupPath, CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Starting user data backup to: {BackupPath}", backupPath);

            // Create backup directory with timestamp
            var timestamp = DateTimeOffset.Now.ToUnixTimeSeconds();
            var fullBackupPath = Path.Combine(backupPath, $"backup_{timestamp}");
            Directory.CreateDirectory(fullBackupPath);

            foreach (var dataPath in dataPaths)
            {
                cancellationToken.ThrowIfCancellationRequested();

                if (!Directory.Exists(dataPath) && !File.Exists(dataPath))
                {
                    _logger.LogWarning("Data path does not exist: {Path}", dataPath);
                    continue;
                }

                var dataName = Path.GetFileName(dataPath);
                var backupItemPath = Path.Combine(fullBackupPath, dataName);

                if (Directory.Exists(dataPath))
                {
                    // Copy directory
                    await CopyDirectoryAsync(dataPath, backupItemPath, cancellationToken);
                    _logger.LogInformation("Backed up directory: {Source} -> {Target}", dataPath, backupItemPath);
                }
                else if (File.Exists(dataPath))
                {
                    // Copy file
                    var targetDir = Path.GetDirectoryName(backupItemPath);
                    if (!string.IsNullOrEmpty(targetDir))
                    {
                        Directory.CreateDirectory(targetDir);
                    }

                    File.Copy(dataPath, backupItemPath, true);
                    _logger.LogInformation("Backed up file: {Source} -> {Target}", dataPath, backupItemPath);
                }
            }

            _logger.LogInformation("User data backup completed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during user data backup");
            throw;
        }
    }

    /// <inheritdoc/>
    public async Task RestoreAsync(string backupPath, string[] dataPaths, CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Starting user data restore from: {BackupPath}", backupPath);

            // Find the most recent backup
            var backupDirs = Directory.GetDirectories(backupPath, "backup_*")
                .OrderByDescending(d => d)
                .ToArray();

            if (backupDirs.Length == 0)
            {
                _logger.LogWarning("No backup directories found");
                return;
            }

            var latestBackup = backupDirs[0];
            _logger.LogInformation("Using latest backup: {Backup}", latestBackup);

            foreach (var dataPath in dataPaths)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var dataName = Path.GetFileName(dataPath);
                var backupItemPath = Path.Combine(latestBackup, dataName);

                if (!Directory.Exists(backupItemPath) && !File.Exists(backupItemPath))
                {
                    _logger.LogWarning("Backup item does not exist: {Path}", backupItemPath);
                    continue;
                }

                if (Directory.Exists(backupItemPath))
                {
                    // Remove existing directory if it exists
                    if (Directory.Exists(dataPath))
                    {
                        Directory.Delete(dataPath, true);
                    }

                    // Restore directory
                    await CopyDirectoryAsync(backupItemPath, dataPath, cancellationToken);
                    _logger.LogInformation("Restored directory: {Source} -> {Target}", backupItemPath, dataPath);
                }
                else if (File.Exists(backupItemPath))
                {
                    // Ensure target directory exists
                    var targetDir = Path.GetDirectoryName(dataPath);
                    if (!string.IsNullOrEmpty(targetDir))
                    {
                        Directory.CreateDirectory(targetDir);
                    }

                    // Restore file
                    File.Copy(backupItemPath, dataPath, true);
                    _logger.LogInformation("Restored file: {Source} -> {Target}", backupItemPath, dataPath);
                }
            }

            // Clean up backup directory
            try
            {
                Directory.Delete(latestBackup, true);
                _logger.LogInformation("Backup directory cleaned up: {Path}", latestBackup);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to clean up backup directory: {Path}", latestBackup);
            }

            _logger.LogInformation("User data restore completed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during user data restore");
            throw;
        }
    }

    private async Task CopyDirectoryAsync(string sourceDir, string targetDir, CancellationToken cancellationToken)
    {
        // Create target directory
        Directory.CreateDirectory(targetDir);

        // Copy all files and subdirectories
        foreach (var file in Directory.GetFiles(sourceDir, "*", SearchOption.AllDirectories))
        {
            cancellationToken.ThrowIfCancellationRequested();

            var relativePath = Path.GetRelativePath(sourceDir, file);
            var targetPath = Path.Combine(targetDir, relativePath);

            var targetFileDir = Path.GetDirectoryName(targetPath);
            if (!string.IsNullOrEmpty(targetFileDir))
            {
                Directory.CreateDirectory(targetFileDir);
            }

            File.Copy(file, targetPath, true);
        }
    }
}
