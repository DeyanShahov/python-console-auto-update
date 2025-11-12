# AutoUpdate Library

A .NET library for implementing automatic updates from GitHub repositories in ASP.NET Core applications.

## Features

- **Automatic Update Checking**: Check for new versions from GitHub repositories
- **Safe Updates**: Backup and restore user data during updates
- **GitHub Integration**: Direct integration with GitHub releases and branches
- **ASP.NET Core Ready**: Built with dependency injection and logging
- **Configurable**: Highly configurable for different project needs
- **Async/Await**: Fully asynchronous operations with cancellation support

## Installation

Add the library to your project by referencing the compiled DLL or by adding it as a NuGet package (when published).

## Quick Start

### 1. Add Services to Program.cs

```csharp
using AutoUpdate.Extensions;

var builder = WebApplication.CreateBuilder(args);

// Add AutoUpdate services with default configuration
builder.Services.AddAutoUpdate("your-github-username", "your-repo-name");

// Or with custom configuration
builder.Services.AddAutoUpdate(options =>
{
    options.GitHubOwner = "your-github-username";
    options.GitHubRepo = "your-repo-name";
    options.ProductionBranch = "user-branch";
    options.DevelopmentBranch = "main-dev";
    options.UserDataPaths = new[] { "App_Data", "wwwroot/uploads" };
    options.VersionFilePath = "version.json";
    options.BackupDirectory = "Backup";
});

var app = builder.Build();
```

### 2. Use in Controllers

```csharp
using AutoUpdate.Services;
using AutoUpdate.Models;

public class HomeController : Controller
{
    private readonly IAutoUpdateService _updateService;

    public HomeController(IAutoUpdateService updateService)
    {
        _updateService = updateService;
    }

    public async Task<IActionResult> Index()
    {
        // Check for updates on page load
        var updateCheck = await _updateService.CheckForUpdatesAsync();
        if (updateCheck.HasUpdate)
        {
            ViewBag.UpdateAvailable = $"New version {updateCheck.NewVersion?.Version} available!";
            ViewBag.ReleaseNotes = updateCheck.ReleaseNotes;
        }

        return View();
    }

    [HttpPost]
    public async Task<IActionResult> ApplyUpdate()
    {
        var result = await _updateService.ApplyUpdateAsync();
        if (result.IsSuccess)
        {
            TempData["Message"] = "Update applied successfully! Please restart the application.";
            return RedirectToAction("Index");
        }

        ModelState.AddModelError("", $"Update failed: {result.ErrorMessage}");
        return View();
    }
}
```

### 3. Version File Format

Create a `version.json` file in your project root:

```json
{
  "version": "1.0.0",
  "commit_sha": "abc123...",
  "last_updated": "2025-01-01",
  "release_notes": "Initial release"
}
```

## Configuration Options

| Property | Description | Default |
|----------|-------------|---------|
| `GitHubOwner` | GitHub username or organization | (required) |
| `GitHubRepo` | Repository name | (required) |
| `ProductionBranch` | Branch for production releases | `"main"` |
| `DevelopmentBranch` | Branch for development | `"main"` |
| `UserDataPaths` | Paths to backup during updates | `[]` |
| `VersionFilePath` | Path to version.json file | `"version.json"` |
| `BackupDirectory` | Directory for backups | `"Backup"` |
| `HttpTimeoutSeconds` | HTTP request timeout | `30` |
| `EnableAutoCheckOnStartup` | Auto-check on app start | `true` |
| `AutoApplyUpdates` | Auto-apply found updates | `false` |

## Architecture

The library follows a modular architecture with clear separation of concerns:

- **IAutoUpdateService**: Main service interface
- **IVersionProvider**: Handles version information retrieval
- **IUpdateDownloader**: Manages download and file application
- **IUserDataManager**: Handles backup and restore operations

All services are registered with dependency injection and can be easily mocked for testing.

## GitHub Repository Setup

1. **Create two branches:**
   - `main-dev` (or your dev branch) - for development
   - `user-branch` (or your production branch) - for user releases

2. **Version file**: Keep `version.json` in both branches

3. **Release process:**
   - Develop features in `main-dev`
   - When ready for release: merge to `user-branch`
   - Update version.json in `user-branch`
   - Push to trigger user updates

## User Data Protection

The library automatically:
1. Backs up specified directories before updates
2. Applies new files (excluding user data)
3. Restores user data after successful update
4. Cleans up backups after successful restore

## Error Handling

- Network failures are logged and handled gracefully
- Failed updates trigger automatic rollback
- User data is always protected during failures
- Comprehensive logging for troubleshooting

## Security Considerations

- Only downloads from specified GitHub repository
- Validates SSL certificates for HTTPS requests
- No execution of downloaded code without explicit application restart
- User data paths are configurable to prevent accidental data loss

## Example Project Structure

```
YourApp/
├── Controllers/
│   └── HomeController.cs (inject IAutoUpdateService)
├── wwwroot/
├── App_Data/ (user data - backed up)
├── version.json
├── Program.cs (register services)
└── YourApp.csproj
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure the application has write permissions to the application directory
2. **Network Timeout**: Check firewall settings and GitHub accessibility
3. **Version File Not Found**: Ensure `version.json` exists in the repository root
4. **Backup Directory Access**: Ensure write permissions for backup operations

### Logging

Enable detailed logging to troubleshoot issues:

```csharp
builder.Logging.AddConsole();
builder.Logging.SetMinimumLevel(LogLevel.Debug);
```

## Contributing

This library is designed to be extensible. You can implement custom providers by inheriting from the interfaces:

- Implement `IVersionProvider` for different version sources
- Implement `IUpdateDownloader` for different download mechanisms
- Implement `IUserDataManager` for custom backup strategies

## License

[Your License Here]
