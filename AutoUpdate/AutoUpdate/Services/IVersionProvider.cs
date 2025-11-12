using AutoUpdate.Models;

namespace AutoUpdate.Services;

/// <summary>
/// Interface for providing version information.
/// </summary>
public interface IVersionProvider
{
    /// <summary>
    /// Gets the local version information asynchronously.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The local version information.</returns>
    Task<VersionInfo> GetLocalVersionAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the remote version information from GitHub asynchronously.
    /// </summary>
    /// <param name="owner">The repository owner.</param>
    /// <param name="repo">The repository name.</param>
    /// <param name="branch">The branch to check.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The remote version information.</returns>
    Task<VersionInfo?> GetRemoteVersionAsync(string owner, string repo, string branch, CancellationToken cancellationToken = default);
}
