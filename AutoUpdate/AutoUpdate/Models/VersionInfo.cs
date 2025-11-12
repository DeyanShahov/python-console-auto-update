using System.Text.Json.Serialization;

namespace AutoUpdate.Models;

/// <summary>
/// Represents version information for the application.
/// </summary>
public class VersionInfo
{
    /// <summary>
    /// The version string (e.g., "1.0.0")
    /// </summary>
    [JsonPropertyName("version")]
    public string Version { get; set; } = "0.0.0";

    /// <summary>
    /// The commit SHA
    /// </summary>
    [JsonPropertyName("commit_sha")]
    public string CommitSha { get; set; } = string.Empty;

    /// <summary>
    /// The last updated date
    /// </summary>
    [JsonPropertyName("last_updated")]
    public string LastUpdated { get; set; } = string.Empty;

    /// <summary>
    /// Release notes for this version
    /// </summary>
    [JsonPropertyName("release_notes")]
    public string ReleaseNotes { get; set; } = string.Empty;

    /// <summary>
    /// Compares this version with another version
    /// </summary>
    /// <param name="other">The other version to compare with</param>
    /// <returns>1 if this version is greater, -1 if less, 0 if equal</returns>
    public int CompareTo(VersionInfo other)
    {
        if (other == null) return 1;

        var thisVersion = System.Version.Parse(Version);
        var otherVersion = System.Version.Parse(other.Version);

        return thisVersion.CompareTo(otherVersion);
    }

    /// <summary>
    /// Determines if this version is greater than the specified version
    /// </summary>
    public bool IsGreaterThan(VersionInfo other)
    {
        return CompareTo(other) > 0;
    }

    /// <summary>
    /// Determines if this version is less than the specified version
    /// </summary>
    public bool IsLessThan(VersionInfo other)
    {
        return CompareTo(other) < 0;
    }

    /// <summary>
    /// Determines if this version equals the specified version
    /// </summary>
    public bool Equals(VersionInfo other)
    {
        return CompareTo(other) == 0;
    }
}
