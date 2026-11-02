<#
  Builds the multilingual MSI (called by `just build-windows`):
  1. builds Package.wxs once per culture with l10n/<culture>.wxl,
  2. derives a code-page-neutral base from the en-US MSI (ASCII-only language names,
     code page 0): a transform can't change a fixed code page, but it can give a
     neutral database one (1252 for Western, 1250 for Central European languages),
  3. creates a language transform (.mst) from the base to every culture's MSI
     (en-US too) and embeds them into the base, named by their LCID, and lists all
     LCIDs in the summary information (Template). Windows Installer then applies the
     transform matching the Windows display language automatically (also for /qn);
     TRANSFORMS=:<LCID> forces one. Other display languages get the neutral base
     (English with "Cestina", "Espanol", "Francais", ... in the language list),
  4. checks every transform by applying it to a copy of the result.
#>
param(
    [Parameter(Mandatory)][string]$Version,
    [Parameter(Mandatory)][string]$PayloadDir,
    [Parameter(Mandatory)][string]$Output
)

$ErrorActionPreference = 'Stop'

# Windows Installer (COM) resolves relative paths against the process directory: use absolute ones.
function Get-FullPath([string]$Path) { $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path) }
$PayloadDir = Get-FullPath $PayloadDir
$Output = Get-FullPath $Output

# Culture -> LCID.
$cultures = [ordered]@{
    'en-US' = 1033; 'de-DE' = 1031; 'fr-FR' = 1036; 'it-IT' = 1040; 'es-ES' = 3082
    'pt-PT' = 2070; 'nl-NL' = 1043; 'nb-NO' = 1044; 'sv-SE' = 1053; 'fi-FI' = 1035
    'cs-CZ' = 1029; 'pl-PL' = 1045; 'hr-HR' = 1050
}
$codepage1250 = 'cs-CZ', 'pl-PL', 'hr-HR'
# Further display languages that get the transform of another culture.
$aliases = @{ 2058 = 'es-ES' <# es-MX #>; 3084 = 'fr-FR' <# fr-CA #> }
# Non-ASCII language names of the language list (Package.wxs) -> ASCII spelling for the neutral base.
$asciiNames = @{ 'cs' = 'Cestina'; 'es' = 'Espanol'; 'fr' = 'Francais'; 'pt' = 'Portugues' }

$installerDir = $PSScriptRoot
$work = [string](Join-Path (Split-Path -Parent $Output) 'windows\msi')
New-Item -ItemType Directory -Force $work | Out-Null

function Invoke-Native([string]$Description, [scriptblock]$Command) {
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "$Description failed with exit code $LASTEXITCODE" }
}

function Invoke-Com($Object, [string]$Name, [string]$Kind, [object[]]$Arguments = @()) {
    # Pass plain .NET values: PowerShell-wrapped ones (PSObject) cause DISP_E_TYPEMISMATCH.
    $plain = [object[]]::new($Arguments.Count)
    for ($i = 0; $i -lt $Arguments.Count; $i++) {
        $value = $Arguments[$i]
        $plain[$i] = if ($value -is [System.Management.Automation.PSObject]) { $value.PSObject.BaseObject } else { $value }
    }
    try {
        $Object.GetType().InvokeMember($Name, [System.Reflection.BindingFlags]$Kind, $null, $Object, $plain)
    } catch {
        throw "Windows Installer $Name($($plain -join ', ')) failed: $($_.Exception.InnerException.Message ?? $_.Exception.Message)"
    }
}

function Release($ComObject) {
    if ($ComObject) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($ComObject) }
}

$installer = New-Object -ComObject WindowsInstaller.Installer
$msiOpenDatabaseModeTransact = 1
$msiViewModifyAssign = 3
$pidTemplate = 7

function Open-Database([string]$Path) { Invoke-Com $installer OpenDatabase InvokeMethod @($Path, $msiOpenDatabaseModeTransact) }

function Invoke-Sql($Database, [string]$Query) {
    $view = Invoke-Com $Database OpenView InvokeMethod @($Query)
    Invoke-Com $view Execute InvokeMethod | Out-Null
    Invoke-Com $view Close InvokeMethod | Out-Null
    Release $view
}

function Get-Value($Database, [string]$Query) {
    $view = Invoke-Com $Database OpenView InvokeMethod @($Query)
    Invoke-Com $view Execute InvokeMethod | Out-Null
    $record = Invoke-Com $view Fetch InvokeMethod
    $value = if ($record) { Invoke-Com $record StringData GetProperty @(1) } else { $null }
    Invoke-Com $view Close InvokeMethod | Out-Null
    Release $view
    $value
}

function Get-LanguageName($Database, [string]$Code) {
    Get-Value $Database "SELECT ``Text`` FROM ``ComboBox`` WHERE ``Property`` = 'APPLANGUAGE' AND ``Value`` = '$Code'"
}

# --- 1. One MSI per culture ---
# One product code for all cultures of this build (otherwise every transform would change it).
$productCode = [guid]::NewGuid().ToString('B').ToUpperInvariant()
foreach ($culture in $cultures.Keys) {
    Invoke-Native "wix build ($culture)" {
        wix build (Join-Path $installerDir 'Package.wxs') -arch x64 `
            -ext WixToolset.Util.wixext -ext WixToolset.UI.wixext `
            -culture $culture -loc (Join-Path $installerDir "l10n/$culture.wxl") `
            -d Version=$Version -d ProductCode=$productCode -bindpath payload=$PayloadDir `
            -o (Join-Path $work "$culture.msi")
    }
}

# --- 2. Code-page-neutral base ---
$base = [string](Join-Path $work 'neutral.msi')
Copy-Item (Join-Path $work 'en-US.msi') $base -Force
$database = Open-Database $base
foreach ($code in $asciiNames.Keys) {
    Invoke-Sql $database "UPDATE ``ComboBox`` SET ``Text`` = '$($asciiNames[$code])' WHERE ``Property`` = 'APPLANGUAGE' AND ``Value`` = '$code'"
}
# A database's code page is set by importing the _ForceCodepage pseudo table.
[System.IO.File]::WriteAllText((Join-Path $work '_ForceCodepage.idt'), "`r`n`r`n0`t_ForceCodepage`r`n", [System.Text.Encoding]::ASCII)
Invoke-Com $database Import InvokeMethod @($work, '_ForceCodepage.idt') | Out-Null
Invoke-Com $database Commit InvokeMethod | Out-Null
Release $database

# --- 3. Language transforms, embedded into a copy of the base ---
# LCID (as string: an [ordered] dictionary indexed with an int returns the n-th entry) -> .mst
$transforms = [ordered]@{}
foreach ($culture in $cultures.Keys) {
    $mst = Join-Path $work "$culture.mst"
    Invoke-Native "wix msi transform ($culture)" {
        wix msi transform -t language -o $mst $base (Join-Path $work "$culture.msi")
    }
    $transforms["$($cultures[$culture])"] = $mst
}
foreach ($lcid in $aliases.Keys) {
    $transforms["$lcid"] = $transforms["$($cultures[$aliases[$lcid]])"]
}

Copy-Item $base $Output -Force
$database = Open-Database $Output
$view = Invoke-Com $database OpenView InvokeMethod @('SELECT `Name`, `Data` FROM `_Storages`')
Invoke-Com $view Execute InvokeMethod | Out-Null
foreach ($lcid in $transforms.Keys) {
    $record = Invoke-Com $installer CreateRecord InvokeMethod @(2)
    Invoke-Com $record StringData SetProperty @(1, $lcid) | Out-Null
    Invoke-Com $record SetStream InvokeMethod @(2, $transforms[$lcid]) | Out-Null
    Invoke-Com $view Modify InvokeMethod @($msiViewModifyAssign, $record) | Out-Null
}
Invoke-Com $view Close InvokeMethod | Out-Null
Release $view

$summary = Invoke-Com $database SummaryInformation GetProperty @(1)
$template = Invoke-Com $summary Property GetProperty @($pidTemplate)   # e.g. "x64;1033"
$platform = $template.Split(';')[0]
$languages = @($transforms.Keys)   # 1033 (en-US) first
Invoke-Com $summary Property SetProperty @($pidTemplate, "$platform;$($languages -join ',')") | Out-Null
Invoke-Com $summary Persist InvokeMethod | Out-Null
Invoke-Com $database Commit InvokeMethod | Out-Null
Release $summary
Release $database

# --- 4. Check every transform: language, app language default and localized language names ---
foreach ($culture in $cultures.Keys) {
    $lcid = $cultures[$culture]
    # The copy stays in the intermediate folder (COM may still hold it open).
    $copy = Join-Path $work "check-$culture.msi"
    Copy-Item $Output $copy -Force
    $db = Open-Database $copy
    Invoke-Com $db ApplyTransform InvokeMethod @($transforms["$lcid"], 0) | Out-Null
    $productLanguage = Get-Value $db "SELECT ``Value`` FROM ``Property`` WHERE ``Property`` = 'ProductLanguage'"
    $transformedProductCode = Get-Value $db "SELECT ``Value`` FROM ``Property`` WHERE ``Property`` = 'ProductCode'"
    $appLanguage = Get-Value $db "SELECT ``Value`` FROM ``Property`` WHERE ``Property`` = 'APPLANGUAGE'"
    $names = '{0}/{1}/{2}/{3}' -f (Get-LanguageName $db 'cs'), (Get-LanguageName $db 'es'), (Get-LanguageName $db 'fr'), (Get-LanguageName $db 'pt')
    Release $db

    $expectedNames = if ($culture -in $codepage1250) { 'Čeština/Espanol/Français/Portugues' } else { 'Cestina/Español/Français/Português' }
    if ($transformedProductCode -ne $productCode) { throw "Transform $culture changes the product code to $transformedProductCode" }
    if ($productLanguage -ne "$lcid" -or $appLanguage -ne $culture.Split('-')[0] -or $names -cne $expectedNames) {
        throw "Transform $culture is broken: ProductLanguage=$productLanguage APPLANGUAGE=$appLanguage names=$names"
    }
    Write-Host "Transform $culture ($lcid) OK: APPLANGUAGE=$appLanguage, names=$names"
}
Release $installer
[GC]::Collect()
[GC]::WaitForPendingFinalizers()

Write-Host "Built $Output (version $Version, languages $($languages -join ','))"
