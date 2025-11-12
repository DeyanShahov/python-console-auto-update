namespace AutoUpdate.Models;

/// <summary>
/// Represents the result of an update operation.
/// </summary>
public class UpdateResult
{
    /// <summary>
    /// Indicates whether the update was successful.
    /// </summary>
    public bool IsSuccess { get; set; }

    /// <summary>
    /// Error message if the update failed.
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// The version that was updated to.
    /// </summary>
    public VersionInfo? UpdatedVersion { get; set; }

    /// <summary>
    /// Creates a successful update result.
    /// </summary>
    /// <param name="updatedVersion">The version that was updated to.</param>
    /// <returns>A successful UpdateResult.</returns>
    public static UpdateResult Success(VersionInfo? updatedVersion = null)
    {
        return new UpdateResult
        {
            IsSuccess = true,
            UpdatedVersion = updatedVersion
        };
    }

    /// <summary>
    /// Creates a failed update result.
    /// </summary>
    /// <param name="errorMessage">The error message.</param>
    /// <returns>A failed UpdateResult.</returns>
    public static UpdateResult Failure(string errorMessage)
    {
        return new UpdateResult
        {
            IsSuccess = false,
            ErrorMessage = errorMessage
        };
    }
}
