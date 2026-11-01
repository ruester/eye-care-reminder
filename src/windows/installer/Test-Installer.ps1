<#
  Installer test used by CI (Windows, elevated):
  1. installs OldMsi with the Czech language transform and starts the tray app
     -> Czech product language, app language "cs",
  2. upgrades to NewMsi while the app runs -> must succeed without reboot,
     close the app, leave exactly one installed product and keep the app language,
  3. starts the app again and uninstalls while it runs -> must remove everything.
#>
param(
    [Parameter(Mandatory)][string]$OldMsi,
    [Parameter(Mandatory)][string]$NewMsi,
    [Parameter(Mandatory)][string]$ExpectedVersion
)

$ErrorActionPreference = 'Stop'
$exe = Join-Path $env:ProgramFiles 'Eye Care Reminder\EyeCareReminder.exe'

function Write-Step([string]$Message) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message"
}

function Invoke-Msi([string]$Action, [string]$Msi, [string]$Log, [string]$Properties = '') {
    Write-Step "msiexec $Action $Msi $Properties"
    # WaitForExit instead of -Wait: -Wait also waits for every process msiexec started.
    $process = Start-Process msiexec.exe -ArgumentList "$Action `"$Msi`" $Properties /qn /l*v `"$Log`"" -PassThru
    if (-not $process.WaitForExit(5 * 60 * 1000)) {
        Get-Content $Log -Tail 60 -ErrorAction SilentlyContinue
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "msiexec $Action $Msi did not finish within 5 minutes"
    }
    if ($process.ExitCode -ne 0) {
        # Show what failed: the lines leading up to the first failing action.
        $failure = Select-String -Path $Log -Pattern 'Return value 3' | Select-Object -First 1
        if ($failure) {
            Get-Content $Log | Select-Object -Skip ([Math]::Max(0, $failure.LineNumber - 40)) -First 42
        } else {
            Get-Content $Log -Tail 60
        }
        throw "msiexec $Action $Msi failed with exit code $($process.ExitCode) (3010 = reboot required)"
    }
}

function Start-App {
    Write-Step "Starting $exe"
    Start-Process $exe -ArgumentList '--autostart'
    Start-Sleep -Seconds 3
    Assert-AppRunning $true
}

function Assert-AppRunning([bool]$Expected) {
    $running = [bool](Get-Process EyeCareReminder -ErrorAction SilentlyContinue)
    if ($running -ne $Expected) { throw "Expected the app to be running: $Expected, actual: $running" }
}

function Get-AppLanguage {
    (Get-ItemProperty 'HKCU:\Software\EyeCareReminder' -Name Language -ErrorAction SilentlyContinue).Language
}

function Assert-AppLanguage([string]$Expected) {
    [string]$actual = Get-AppLanguage
    if ($actual -ne $Expected) { throw "Expected app language '$Expected', found '$actual'" }
}

function Get-InstalledProducts {
    @(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' |
        Where-Object { $_.DisplayName -eq 'Eye Care Reminder' })
}

Write-Step "Installing $OldMsi"
Invoke-Msi '/i' $OldMsi 'install-old.log' 'TRANSFORMS=:1029'
Select-String -Path 'install-old.log' -Pattern 'transform|APPLANGUAGE|ProductLanguage' | Select-Object -First 20 |
    ForEach-Object { Write-Host "  log: $($_.Line.Trim())" }
Write-Step "Registered product language: $((Get-InstalledProducts).Language)"
# APPLANGUAGE defaults to the language of the applied transform.
Assert-AppLanguage 'cs'
Start-App

Write-Step "Upgrading to $NewMsi while the app is running"
Invoke-Msi '/i' $NewMsi 'upgrade.log'
Assert-AppRunning $false
$products = Get-InstalledProducts
if ($products.Count -ne 1) { throw "Expected 1 installed product after upgrade, found $($products.Count)" }
$fileVersion = (Get-Item $exe).VersionInfo.FileVersion
if (-not $fileVersion.StartsWith($ExpectedVersion)) { throw "Expected version $ExpectedVersion, installed $fileVersion" }
Assert-AppLanguage 'cs'

Write-Step 'Uninstalling while the app is running'
Start-App
Invoke-Msi '/x' $NewMsi 'uninstall.log'
Assert-AppRunning $false
if (Test-Path $exe) { throw "$exe still exists after uninstall" }
if ((Get-InstalledProducts).Count -ne 0) { throw 'Product still registered after uninstall' }
Assert-AppLanguage $null

Write-Step 'Installer test passed'
