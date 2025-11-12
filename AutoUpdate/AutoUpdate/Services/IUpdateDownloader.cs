namespace AutoUpdate.Services;

/// <summary>
/// Interface for downloading and applying updates.
/// </summary>
public interface IUpdateDownloader
{
    /// <summary>
    /// Downloads and extracts the update archive asynchronously.
    /// </summary>
    /// <param name="owner">The repository owner.</param>
    /// <param name="repo">The repository name.</param>
    /// <param name="branch">The branch to download from.</param>
    /// <param name="tempPath">The temporary path to extract to.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The path where the update was extracted.</returns>
    Task<string> DownloadAndExtractAsync(string owner, string repo, string branch, string tempPath, CancellationToken cancellationToken = default);

    /// <summary>
    /// Applies the downloaded files to the application directory asynchronously.
    /// </summary>
    /// <param name="sourcePath">The source path of extracted files.</param>
    /// <param name="excludePaths">Paths to exclude from copying.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task ApplyFilesAsync(string sourcePath, string[] excludePaths, CancellationToken cancellationToken = default);
}
