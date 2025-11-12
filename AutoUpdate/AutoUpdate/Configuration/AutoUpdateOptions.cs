namespace AutoUpdate.Configuration;

/// <summary>
/// Configuration options for the AutoUpdate service.
/// </summary>
public class AutoUpdateOptions
{
    /// <summary>
    /// The GitHub repository owner (username or organization).
    /// </summary>
    public string GitHubOwner { get; set; } = string.Empty;

    /// <summary>
    /// The GitHub repository name.
    /// </summary>
    public string GitHubRepo { get; set; } = string.Empty;

    /// <summary>
    /// The branch to check for updates (production branch).
    /// </summary>
    public string ProductionBranch { get; set; } = "main";

    /// <summary>
    /// The development branch (for reference).
    /// </summary>
    public string DevelopmentBranch { get; set; } = "main";

    /// <summary>
    /// Paths to user data directories/files that should be backed up and restored.
    /// </summary>
    public string[] UserDataPaths { get; set; } = Array.Empty<string>();

    /// <summary>
    /// Path to the version file.
    /// </summary>
    public string VersionFilePath { get; set; } = "version.json";

    /// <summary>
    /// Directory where backups will be stored.
    /// </summary>
    public string BackupDirectory { get; set; } = "Backup";

    /// <summary>
    /// Timeout for HTTP requests in seconds.
    /// </summary>
    public int HttpTimeoutSeconds { get; set; } = 30;

    /// <summary>
    /// Whether to enable automatic update checks on application startup.
    /// </summary>
    public bool EnableAutoCheckOnStartup { get; set; } = true;

    /// <summary>
    /// Whether to automatically apply updates when found.
    /// </summary>
    public bool AutoApplyUpdates { get; set; } = false;
}
