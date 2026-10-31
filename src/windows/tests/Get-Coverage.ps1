<#
.SYNOPSIS
    Prints the line coverage from the Cobertura report that `just test-windows`
    writes and stores the rounded percentage in <ResultsDir>/coverage-percent.txt.
#>
param(
    [Parameter(Mandatory)] [string] $ResultsDir
)

$ErrorActionPreference = 'Stop'

$report = Get-ChildItem $ResultsDir -Recurse -Filter *.cobertura.xml | Select-Object -First 1
if (-not $report) {
    throw "No Cobertura coverage report found in $ResultsDir"
}

$coverage = ([xml](Get-Content -Raw $report.FullName)).coverage
$covered = [int]$coverage.'lines-covered'
$valid = [int]$coverage.'lines-valid'
if ($valid -eq 0) {
    throw "Coverage report $($report.FullName) contains no lines"
}

$percent = 100.0 * $covered / $valid
Write-Host ("Line coverage: {0:N1}% ({1} of {2} lines)" -f $percent, $covered, $valid)
Set-Content (Join-Path $ResultsDir coverage-percent.txt) ([int][Math]::Floor($percent))
