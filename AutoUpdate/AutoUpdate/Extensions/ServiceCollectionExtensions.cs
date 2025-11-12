using AutoUpdate.Configuration;
using AutoUpdate.Services;
using Microsoft.Extensions.DependencyInjection;

namespace AutoUpdate.Extensions;

/// <summary>
/// Extension methods for configuring AutoUpdate services.
/// </summary>
public static class ServiceCollectionExtensions
{
    /// <summary>
    /// Adds AutoUpdate services to the dependency injection container.
    /// </summary>
    /// <param name="services">The service collection.</param>
    /// <param name="configureOptions">Action to configure the AutoUpdate options.</param>
    /// <returns>The service collection for chaining.</returns>
    public static IServiceCollection AddAutoUpdate(
        this IServiceCollection services,
        Action<AutoUpdateOptions> configureOptions)
    {
        // Configure options
        services.Configure(configureOptions);

        // Register HTTP client for GitHub API calls
        services.AddHttpClient();

        // Register services
        services.AddScoped<IVersionProvider, VersionProvider>();
        services.AddScoped<IUpdateDownloader, UpdateDownloader>();
        services.AddScoped<IUserDataManager, UserDataManager>();
        services.AddScoped<IAutoUpdateService, AutoUpdateService>();

        return services;
    }

    /// <summary>
    /// Adds AutoUpdate services with default configuration for AI-Online-Radio project.
    /// </summary>
    /// <param name="services">The service collection.</param>
    /// <param name="gitHubOwner">GitHub repository owner.</param>
    /// <param name="gitHubRepo">GitHub repository name.</param>
    /// <param name="productionBranch">Production branch name (default: "user-branch").</param>
    /// <param name="developmentBranch">Development branch name (default: "main-dev").</param>
    /// <returns>The service collection for chaining.</returns>
    public static IServiceCollection AddAutoUpdate(
        this IServiceCollection services,
        string gitHubOwner,
        string gitHubRepo,
        string productionBranch = "user-branch",
        string developmentBranch = "main-dev")
    {
        return services.AddAutoUpdate(options =>
        {
            options.GitHubOwner = gitHubOwner;
            options.GitHubRepo = gitHubRepo;
            options.ProductionBranch = productionBranch;
            options.DevelopmentBranch = developmentBranch;
            options.UserDataPaths = new[] { "App_Data", "wwwroot/uploads" };
            options.VersionFilePath = "version.json";
            options.BackupDirectory = "Backup";
        });
    }
}
