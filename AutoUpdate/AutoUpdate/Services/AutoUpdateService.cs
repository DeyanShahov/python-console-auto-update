using AutoUpdate.Configuration;
using AutoUpdate.Models;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AutoUpdate.Services;

/// <summary>
/// Main implementation of IAutoUpdateService that orchestrates the update process.
/// </summary>
public class AutoUpdateService : IAutoUpdateService
{
    private readonly AutoUpdateOptions _options;
    private readonly IVersionProvider _versionProvider;
    private readonly IUpdateDownloader _updateDownloader;
    private readonly IUserDataManager _userDataManager;
    private readonly ILogger<AutoUpdateService> _logger;

    public AutoUpdateService(
        IOptions<AutoUpdateOptions> options,
        IVersionProvider versionProvider,
        IUpdateDownloader updateDownloader,
        IUserDataManager userDataManager,
        ILogger<AutoUpdateService> logger)
    {
        _options = options.Value;
        _versionProvider = versionProvider;
        _updateDownloader = updateDownloader;
        _userDataManager = userDataManager;
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task<UpdateCheckResult> CheckForUpdatesAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Checking for updates from GitHub repository: {Owner}/{Repo} branch: {Branch}",
                _options.GitHubOwner, _options.GitHubRepo, _options.ProductionBranch);

            // Get local and remote versions
            var localVersion = await _versionProvider.GetLocalVersionAsync(cancellationToken);
            var remoteVersion = await _versionProvider.GetRemoteVersionAsync(
                _options.GitHubOwner,
                _options.GitHubRepo,
                _options.ProductionBranch,
                cancellationToken);

            if (remoteVersion == null)
            {
                _logger.LogWarning("Failed to fetch remote version information");
                return UpdateCheckResult.NoUpdate(localVersion);
            }

            // Compare versions
            if (remoteVersion.IsGreaterThan(localVersion))
            {
                _logger.LogInformation("Update available: {Current} -> {New}",
                    localVersion.Version, remoteVersion.Version);
                return UpdateCheckResult.UpdateAvailable(localVersion, remoteVersion);
            }
            else
            {
                _logger.LogInformation("Application is up to date: {Version}", localVersion.Version);
                return UpdateCheckResult.NoUpdate(localVersion);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking for updates");
            // Return no update available on error
            var localVersion = await _versionProvider.GetLocalVersionAsync(cancellationToken);
            return UpdateCheckResult.NoUpdate(localVersion);
        }
    }

    /// <inheritdoc/>
    public async Task<UpdateResult> ApplyUpdateAsync(CancellationToken cancellationToken = default)
    {
        var tempPath = Path.Combine(Path.GetTempPath(), $"AutoUpdate_{Guid.NewGuid()}");

        try
        {
            _logger.LogInformation("Starting update process");

            // 1. Get remote version info
            var remoteVersion = await _versionProvider.GetRemoteVersionAsync(
                _options.GitHubOwner,
                _options.GitHubRepo,
                _options.ProductionBranch,
                cancellationToken);

            if (remoteVersion == null)
            {
                return UpdateResult.Failure("Failed to fetch remote version information");
            }

            // 2. Backup user data
            _logger.LogInformation("Backing up user data");
            await _userDataManager.BackupAsync(_options.UserDataPaths, _options.BackupDirectory, cancellationToken);

            // 3. Download and extract update
            _logger.LogInformation("Downloading and extracting update");
            var extractedPath = await _updateDownloader.DownloadAndExtractAsync(
                _options.GitHubOwner,
                _options.GitHubRepo,
                _options.ProductionBranch,
                tempPath,
                cancellationToken);

            // 4. Apply update files (exclude user data and version file)
            var excludePaths = _options.UserDataPaths.Concat(new[] { _options.VersionFilePath }).ToArray();
            _logger.LogInformation("Applying update files");
            await _updateDownloader.ApplyFilesAsync(extractedPath, excludePaths, cancellationToken);

            // 5. Update local version file
            _logger.LogInformation("Updating version file to: {Version}", remoteVersion.Version);
            var versionJson = System.Text.Json.JsonSerializer.Serialize(remoteVersion, new System.Text.Json.JsonSerializerOptions
            {
                WriteIndented = true
            });
            await File.WriteAllTextAsync(_options.VersionFilePath, versionJson, cancellationToken);

            // 6. Restore user data
            _logger.LogInformation("Restoring user data");
            await _userDataManager.RestoreAsync(_options.BackupDirectory, _options.UserDataPaths, cancellationToken);

            _logger.LogInformation("Update completed successfully: {Version}", remoteVersion.Version);
            return UpdateResult.Success(remoteVersion);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Update failed, attempting to restore user data");

            // Try to restore user data on failure
            try
            {
                await _userDataManager.RestoreAsync(_options.BackupDirectory, _options.UserDataPaths, cancellationToken);
                _logger.LogInformation("User data restored after failed update");
            }
            catch (Exception restoreEx)
            {
                _logger.LogError(restoreEx, "Failed to restore user data after update failure");
            }

            return UpdateResult.Failure($"Update failed: {ex.Message}");
        }
        finally
        {
            // Clean up temporary files
            try
            {
                if (Directory.Exists(tempPath))
                {
                    Directory.Delete(tempPath, true);
                    _logger.LogDebug("Temporary files cleaned up");
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to clean up temporary files");
            }
        }
    }
}
