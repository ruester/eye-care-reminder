<#
  Builds the multilingual MSI (called by `just build-windows`):
  1. builds Package.wxs once per culture with l10n/<culture>.wxl,
  2. uses the en-US MSI as the base and creates a language transform (.mst) from it
     to every other culture's MSI,
  3. embeds the transforms into the base MSI, named by their LCID, and lists all LCIDs
     in the summary information (Template). Windows Installer then applies the
     transform matching the Windows display language automatically (also for /qn);
     TRANSFORMS=:<LCID> forces one,
  4. checks every transform by applying it to a copy of the base MSI.
#>
param(
    [Parameter(Mandatory)][string]$Version,
    [Parameter(Mandatory)][string]$PayloadDir,
    [Parameter(Mandatory)][string]$Output
)

$ErrorActionPreference = 'Stop'

# Culture -> LCID. en-US is the base (also used for every other display language).
$cultures = [ordered]@{
    'en-US' = 1033; 'de-DE' = 1031; 'fr-FR' = 1036; 'it-IT' = 1040; 'es-ES' = 3082
    'pt-PT' = 2070; 'nl-NL' = 1043; 'nb-NO' = 1044; 'sv-SE' = 1053; 'fi-FI' = 1035
    'cs-CZ' = 1029; 'pl-PL' = 1045; 'hr-HR' = 1050
}
# Further display languages that get the transform of another culture.
$aliases = @{ 2058 = 'es-ES' <# es-MX #>; 3084 = 'fr-FR' <# fr-CA #> }

$installerDir = $PSScriptRoot
$work = Join-Path (Split-Path -Parent $Output) 'windows/msi'
New-Item -ItemType Directory -Force $work | Out-Null

function Invoke-Native([string]$Description, [scriptblock]$Command) {
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "$Description failed with exit code $LASTEXITCODE" }
}

# --- 1. One MSI per culture ---
foreach ($culture in $cultures.Keys) {
    Invoke-Native "wix build ($culture)" {
        wix build (Join-Path $installerDir 'Package.wxs') -arch x64 `
            -ext WixToolset.Util.wixext -ext WixToolset.UI.wixext `
            -culture $culture -loc (Join-Path $installerDir "l10n/$culture.wxl") `
            -d Version=$Version -bindpath payload=$PayloadDir `
            -o (Join-Path $work "$culture.msi")
    }
}

# --- 2. Language transforms against the en-US base ---
$base = Join-Path $work 'en-US.msi'
$transforms = [ordered]@{}
foreach ($culture in $cultures.Keys) {
    if ($culture -eq 'en-US') { continue }
    $mst = Join-Path $work "$culture.mst"
    Invoke-Native "wix msi transform ($culture)" {
        wix msi transform -t language -o $mst $base (Join-Path $work "$culture.msi")
    }
    $transforms[$cultures[$culture]] = $mst
}
foreach ($lcid in $aliases.Keys) {
    $transforms[$lcid] = $transforms[$cultures[$aliases[$lcid]]]
}

# --- 3. Embed the transforms into a copy of the base MSI ---
Copy-Item $base $Output -Force

function Invoke-Com($Object, [string]$Name, [string]$Kind, [object[]]$Arguments = @()) {
    $Object.GetType().InvokeMember($Name, [System.Reflection.BindingFlags]$Kind, $null, $Object, $Arguments)
}

$installer = New-Object -ComObject WindowsInstaller.Installer
$msiOpenDatabaseModeReadOnly = 0
$msiOpenDatabaseModeTransact = 1
$msiViewModifyAssign = 3
$pidTemplate = 7

$database = Invoke-Com $installer OpenDatabase InvokeMethod @($Output, $msiOpenDatabaseModeTransact)
$view = Invoke-Com $database OpenView InvokeMethod @('SELECT `Name`, `Data` FROM `_Storages`')
Invoke-Com $view Execute InvokeMethod | Out-Null
foreach ($lcid in $transforms.Keys) {
    $record = Invoke-Com $installer CreateRecord InvokeMethod @(2)
    Invoke-Com $record StringData SetProperty @(1, [string]$lcid) | Out-Null
    Invoke-Com $record SetStream InvokeMethod @(2, $transforms[$lcid]) | Out-Null
    Invoke-Com $view Modify InvokeMethod @($msiViewModifyAssign, $record) | Out-Null
}
Invoke-Com $view Close InvokeMethod | Out-Null

$summary = Invoke-Com $database SummaryInformation GetProperty @(1)
$template = Invoke-Com $summary Property GetProperty @($pidTemplate)   # e.g. "x64;1033"
$platform = $template.Split(';')[0]
$languages = @(1033) + @($transforms.Keys)
Invoke-Com $summary Property SetProperty @($pidTemplate, "$platform;$($languages -join ',')") | Out-Null
Invoke-Com $summary Persist InvokeMethod | Out-Null
Invoke-Com $database Commit InvokeMethod | Out-Null
[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($view)
[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($summary)
[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($database)

# --- 4. Check every transform: apply it and read back language, default and a localized name ---
function Get-Value($Database, [string]$Query) {
    $v = Invoke-Com $Database OpenView InvokeMethod @($Query)
    Invoke-Com $v Execute InvokeMethod | Out-Null
    $r = Invoke-Com $v Fetch InvokeMethod
    $value = if ($r) { Invoke-Com $r StringData GetProperty @(1) } else { $null }
    Invoke-Com $v Close InvokeMethod | Out-Null
    $value
}

foreach ($culture in $cultures.Keys) {
    if ($culture -eq 'en-US') { continue }
    $lcid = $cultures[$culture]
    $copy = Join-Path $work "check-$culture.msi"
    Copy-Item $base $copy -Force
    $db = Invoke-Com $installer OpenDatabase InvokeMethod @($copy, $msiOpenDatabaseModeTransact)
    Invoke-Com $db ApplyTransform InvokeMethod @($transforms[$lcid], 0) | Out-Null
    $productLanguage = Get-Value $db "SELECT ``Value`` FROM ``Property`` WHERE ``Property`` = 'ProductLanguage'"
    $appLanguage = Get-Value $db "SELECT ``Value`` FROM ``Property`` WHERE ``Property`` = 'APPLANGUAGE'"
    $czechia = Get-Value $db "SELECT ``Text`` FROM ``ComboBox`` WHERE ``Property`` = 'APPLANGUAGE' AND ``Value`` = 'cs'"
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($db)
    Remove-Item $copy

    $expectedCzechia = if ($culture -in 'cs-CZ', 'pl-PL', 'hr-HR') { 'Česko' } else { 'Cesko' }
    if ($productLanguage -ne [string]$lcid -or $appLanguage -ne $culture.Split('-')[0] -or $czechia -ne $expectedCzechia) {
        throw "Transform $culture is broken: ProductLanguage=$productLanguage APPLANGUAGE=$appLanguage Czechia=$czechia"
    }
    Write-Host "Transform $culture ($lcid) OK: APPLANGUAGE=$appLanguage, Czechia=$czechia"
}
[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($installer)
[GC]::Collect()
[GC]::WaitForPendingFinalizers()

Write-Host "Built $Output (version $Version, languages $($languages -join ','))"
