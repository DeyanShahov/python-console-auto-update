using AutoUpdate.Services;
using AutoUpdate.Models;
using Microsoft.AspNetCore.Mvc;

namespace ExampleMVC.Controllers;

public class HomeController : Controller
{
    private readonly ILogger<HomeController> _logger;
    private readonly IAutoUpdateService _updateService;

    public HomeController(
        ILogger<HomeController> logger,
        IAutoUpdateService updateService)
    {
        _logger = logger;
        _updateService = updateService;
    }

    public async Task<IActionResult> Index()
    {
        try
        {
            // Check for updates when the home page loads
            var updateCheck = await _updateService.CheckForUpdatesAsync();

            if (updateCheck.HasUpdate)
            {
                ViewBag.UpdateAvailable = true;
                ViewBag.NewVersion = updateCheck.NewVersion?.Version;
                ViewBag.ReleaseNotes = updateCheck.ReleaseNotes;
                ViewBag.CurrentVersion = updateCheck.CurrentVersion?.Version;

                _logger.LogInformation("Update available: {Current} -> {New}",
                    updateCheck.CurrentVersion?.Version, updateCheck.NewVersion?.Version);
            }
            else
            {
                ViewBag.UpdateAvailable = false;
                ViewBag.CurrentVersion = updateCheck.CurrentVersion?.Version;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking for updates");
            ViewBag.UpdateError = "Unable to check for updates at this time.";
        }

        return View();
    }

    [HttpPost]
    public async Task<IActionResult> CheckForUpdates()
    {
        try
        {
            var updateCheck = await _updateService.CheckForUpdatesAsync();

            if (updateCheck.HasUpdate)
            {
                TempData["UpdateMessage"] = $"New version {updateCheck.NewVersion?.Version} is available!";
                TempData["ReleaseNotes"] = updateCheck.ReleaseNotes;
            }
            else
            {
                TempData["UpdateMessage"] = "Your application is up to date.";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking for updates");
            TempData["UpdateError"] = "Failed to check for updates. Please try again later.";
        }

        return RedirectToAction("Index");
    }

    [HttpPost]
    public async Task<IActionResult> ApplyUpdate()
    {
        try
        {
            _logger.LogInformation("Starting manual update process");

            var result = await _updateService.ApplyUpdateAsync();

            if (result.IsSuccess)
            {
                _logger.LogInformation("Update applied successfully: {Version}", result.UpdatedVersion?.Version);
                TempData["SuccessMessage"] = $"Update to version {result.UpdatedVersion?.Version} applied successfully! Please restart the application to complete the update.";
            }
            else
            {
                _logger.LogError("Update failed: {Error}", result.ErrorMessage);
                TempData["UpdateError"] = $"Update failed: {result.ErrorMessage}";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error during update");
            TempData["UpdateError"] = "An unexpected error occurred during the update process.";
        }

        return RedirectToAction("Index");
    }

    public IActionResult Privacy()
    {
        return View();
    }

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = System.Diagnostics.Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}

// Error View Model (you would typically have this in a separate file)
public class ErrorViewModel
{
    public string? RequestId { get; set; }

    public bool ShowRequestId => !string.IsNullOrEmpty(RequestId);
}
