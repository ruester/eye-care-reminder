<#
  Installer test used by CI (Windows, elevated):
  1. installs OldMsi and starts the tray app,
  2. upgrades to NewMsi while the app runs -> must succeed without reboot,
     close the app and leave exactly one installed product,
  3. starts the app again and uninstalls while it runs -> must remove everything.
#>
param(
    [Parameter(Mandatory)][string]$OldMsi,
    [Parameter(Mandatory)][string]$NewMsi,
    [Parameter(Mandatory)][string]$ExpectedVersion
)

$ErrorActionPreference = 'Stop'
$exe = Join-Path $env:ProgramFiles 'Eye Care Reminder\EyeCareReminder.exe'

function Invoke-Msi([string]$Action, [string]$Msi, [string]$Log) {
    $process = Start-Process msiexec.exe -ArgumentList "$Action `"$Msi`" /qn /l*v `"$Log`"" -Wait -PassThru
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
    Start-Process $exe -ArgumentList '--autostart'
    Start-Sleep -Seconds 3
    Assert-AppRunning $true
}

function Assert-AppRunning([bool]$Expected) {
    $running = [bool](Get-Process EyeCareReminder -ErrorAction SilentlyContinue)
    if ($running -ne $Expected) { throw "Expected the app to be running: $Expected, actual: $running" }
}

function Get-InstalledProducts {
    @(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' |
        Where-Object { $_.DisplayName -eq 'Eye Care Reminder' })
}

Write-Host "Installing $OldMsi"
Invoke-Msi '/i' $OldMsi 'install-old.log'
Start-App

Write-Host "Upgrading to $NewMsi while the app is running"
Invoke-Msi '/i' $NewMsi 'upgrade.log'
Assert-AppRunning $false
$products = Get-InstalledProducts
if ($products.Count -ne 1) { throw "Expected 1 installed product after upgrade, found $($products.Count)" }
$fileVersion = (Get-Item $exe).VersionInfo.FileVersion
if (-not $fileVersion.StartsWith($ExpectedVersion)) { throw "Expected version $ExpectedVersion, installed $fileVersion" }

Write-Host "Uninstalling while the app is running"
Start-App
Invoke-Msi '/x' $NewMsi 'uninstall.log'
Assert-AppRunning $false
if (Test-Path $exe) { throw "$exe still exists after uninstall" }
if ((Get-InstalledProducts).Count -ne 0) { throw 'Product still registered after uninstall' }

Write-Host 'Installer test passed'
