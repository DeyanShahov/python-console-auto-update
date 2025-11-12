namespace AutoUpdate.Models;

/// <summary>
/// Represents the result of checking for updates.
/// </summary>
public class UpdateCheckResult
{
    /// <summary>
    /// Indicates whether an update is available.
    /// </summary>
    public bool HasUpdate { get; set; }

    /// <summary>
    /// The current version of the application.
    /// </summary>
    public VersionInfo? CurrentVersion { get; set; }

    /// <summary>
    /// The new version available for update.
    /// </summary>
    public VersionInfo? NewVersion { get; set; }

    /// <summary>
    /// Release notes for the new version.
    /// </summary>
    public string? ReleaseNotes { get; set; }

    /// <summary>
    /// Creates a result indicating no update is available.
    /// </summary>
    /// <param name="currentVersion">The current version.</param>
    /// <returns>An UpdateCheckResult with no update available.</returns>
    public static UpdateCheckResult NoUpdate(VersionInfo currentVersion)
    {
        return new UpdateCheckResult
        {
            HasUpdate = false,
            CurrentVersion = currentVersion
        };
    }

    /// <summary>
    /// Creates a result indicating an update is available.
    /// </summary>
    /// <param name="currentVersion">The current version.</param>
    /// <param name="newVersion">The new version available.</param>
    /// <returns>An UpdateCheckResult with update available.</returns>
    public static UpdateCheckResult UpdateAvailable(VersionInfo currentVersion, VersionInfo newVersion)
    {
        return new UpdateCheckResult
        {
            HasUpdate = true,
            CurrentVersion = currentVersion,
            NewVersion = newVersion,
            ReleaseNotes = newVersion?.ReleaseNotes
        };
    }
}
