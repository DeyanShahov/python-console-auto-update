using System.Text.Json;
using AutoUpdate.Configuration;
using AutoUpdate.Models;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AutoUpdate.Services;

/// <summary>
/// Implementation of IVersionProvider for GitHub-based version management.
/// </summary>
public class VersionProvider : IVersionProvider
{
    private readonly AutoUpdateOptions _options;
    private readonly ILogger<VersionProvider> _logger;
    private readonly HttpClient _httpClient;

    public VersionProvider(
        IOptions<AutoUpdateOptions> options,
        ILogger<VersionProvider> logger,
        HttpClient httpClient)
    {
        _options = options.Value;
        _logger = logger;
        _httpClient = httpClient;
        _httpClient.Timeout = TimeSpan.FromSeconds(_options.HttpTimeoutSeconds);
    }

    /// <inheritdoc/>
    public async Task<VersionInfo> GetLocalVersionAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            if (!File.Exists(_options.VersionFilePath))
            {
                _logger.LogWarning("Version file not found at {Path}, returning default version", _options.VersionFilePath);
                return new VersionInfo { Version = "0.0.0" };
            }

            var json = await File.ReadAllTextAsync(_options.VersionFilePath, cancellationToken);
            var versionInfo = JsonSerializer.Deserialize<VersionInfo>(json);

            if (versionInfo == null)
            {
                _logger.LogWarning("Failed to deserialize version file, returning default version");
                return new VersionInfo { Version = "0.0.0" };
            }

            _logger.LogInformation("Local version loaded: {Version}", versionInfo.Version);
            return versionInfo;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error reading local version file");
            return new VersionInfo { Version = "0.0.0" };
        }
    }

    /// <inheritdoc/>
    public async Task<VersionInfo?> GetRemoteVersionAsync(string owner, string repo, string branch, CancellationToken cancellationToken = default)
    {
        try
        {
            var versionUrl = $"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{_options.VersionFilePath}";
            _logger.LogInformation("Fetching remote version from: {Url}", versionUrl);

            var response = await _httpClient.GetAsync(versionUrl, cancellationToken);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync(cancellationToken);
            var versionInfo = JsonSerializer.Deserialize<VersionInfo>(json);

            if (versionInfo == null)
            {
                _logger.LogWarning("Failed to deserialize remote version info");
                return null;
            }

            _logger.LogInformation("Remote version fetched: {Version}", versionInfo.Version);
            return versionInfo;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error while fetching remote version");
            return null;
        }
        catch (JsonException ex)
        {
            _logger.LogError(ex, "JSON parsing error while fetching remote version");
            return null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error while fetching remote version");
            return null;
        }
    }
}
