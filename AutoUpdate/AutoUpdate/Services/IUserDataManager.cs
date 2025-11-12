namespace AutoUpdate.Services;

/// <summary>
/// Interface for managing user data backup and restore operations.
/// </summary>
public interface IUserDataManager
{
    /// <summary>
    /// Backs up user data asynchronously.
    /// </summary>
    /// <param name="dataPaths">Paths to the user data directories/files.</param>
    /// <param name="backupPath">Path where to store the backup.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task BackupAsync(string[] dataPaths, string backupPath, CancellationToken cancellationToken = default);

    /// <summary>
    /// Restores user data asynchronously.
    /// </summary>
    /// <param name="backupPath">Path to the backup.</param>
    /// <param name="dataPaths">Paths where to restore the data.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task RestoreAsync(string backupPath, string[] dataPaths, CancellationToken cancellationToken = default);
}
