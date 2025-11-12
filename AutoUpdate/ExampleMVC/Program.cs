using AutoUpdate.Extensions;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews();

// Add AutoUpdate services with configuration for AI-Online-Radio project
builder.Services.AddAutoUpdate("your-github-username", "AI-Online-Radio", "user-branch", "main-dev");

// Or with full custom configuration:
/*
builder.Services.AddAutoUpdate(options =>
{
    options.GitHubOwner = "your-github-username";
    options.GitHubRepo = "AI-Online-Radio";
    options.ProductionBranch = "user-branch";
    options.DevelopmentBranch = "main-dev";
    options.UserDataPaths = new[] { "App_Data", "wwwroot/uploads", "Database" };
    options.VersionFilePath = "version.json";
    options.BackupDirectory = "Backup";
    options.HttpTimeoutSeconds = 30;
    options.EnableAutoCheckOnStartup = true;
    options.AutoApplyUpdates = false;
});
*/

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
