using AutoUpdate.Models;

namespace AutoUpdate.Services;

/// <summary>
/// Interface for the main auto-update service.
/// </summary>
public interface IAutoUpdateService
{
    /// <summary>
    /// Checks for available updates asynchronously.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The result of the update check.</returns>
    Task<UpdateCheckResult> CheckForUpdatesAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Applies available updates asynchronously.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The result of the update operation.</returns>
    Task<UpdateResult> ApplyUpdateAsync(CancellationToken cancellationToken = default);
}
