# PowerShell script for installing Python Console App
# This script downloads and runs the Python install.py script.
# Usage: iex (irm 'https://raw.githubusercontent.com/DeyanShahov/python-console-auto-update/production/install.ps1')

$repoOwner = "DeyanShahov"
$repoName = "python-console-auto-update"
$branch = "production"
$installPyUrl = "https://raw.githubusercontent.com/$repoOwner/$repoName/$branch/install.py"
$tempInstallPyPath = Join-Path $env:TEMP "install.py"

Write-Host "🔄 Изтегляне на инсталационния скрипт..."

try {
    # Download install.py
    Invoke-WebRequest -Uri $installPyUrl -OutFile $tempInstallPyPath -ErrorAction Stop

    Write-Host "✅ Инсталационният скрипт е изтеглен успешно."
    Write-Host "🚀 Стартиране на инсталацията..."

    # Execute install.py using the default Python interpreter
    # This will handle cloning, cleanup, and running the app
    & python $tempInstallPyPath

    # Clean up the temporary install.py script
    Remove-Item $tempInstallPyPath -ErrorAction SilentlyContinue

} catch {
    Write-Host "❌ Грешка по време на инсталацията:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "Моля, уверете се, че Python е инсталиран и достъпен в PATH." -ForegroundColor Yellow
    Write-Host "Можете също да опитате ръчна инсталация, като изтеглите ZIP файла от GitHub." -ForegroundColor Yellow
}
