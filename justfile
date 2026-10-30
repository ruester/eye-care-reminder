# Eye Care Reminder build recipes.
# Release artifacts are written to build/ (ignored by git except build/.keep).

set windows-shell := ["pwsh", "-NoLogo", "-NoProfile", "-Command"]

# Release version, e.g. VERSION=1.2.3 just build-linux. MSI requires x.y.z.
version := env("VERSION", "0.0.0")

linux_bin := "build/eye-care-reminder-linux.bin"
windows_msi := "build/eye-care-reminder-windows-x64.msi"

# List available recipes
default:
    @just --list

# Build the self-extracting Linux installer (.bin)
[unix]
build-linux:
    #!/usr/bin/env bash
    set -euo pipefail
    stage=build/linux/stage
    rm -rf build/linux
    mkdir -p "$stage"
    cp -R src/linux/installer src/linux/freedesktop src/linux/xfce src/linux/unity "$stage/"
    echo "{{version}}" > "$stage/VERSION"
    tar -C "$stage" -czf build/linux/payload.tar.gz .
    cat src/linux/installer/header.sh build/linux/payload.tar.gz > "{{linux_bin}}"
    chmod +x "{{linux_bin}}"
    echo "Built {{linux_bin}} (version {{version}})"

# Build the Windows MSI installer (requires WiX Toolset: dotnet tool install --global wix)
[windows]
build-windows:
    if (Test-Path build/windows) { Remove-Item -Recurse -Force build/windows }
    New-Item -ItemType Directory -Force build/windows/payload | Out-Null
    Copy-Item -Recurse -Path src/windows/app/* -Exclude .keep -Destination build/windows/payload
    Copy-Item README.md build/windows/payload/
    wix build src/windows/installer/Package.wxs -arch x64 -d Version={{version}} -bindpath payload=build/windows/payload -o {{windows_msi}}
    Write-Host "Built {{windows_msi}} (version {{version}})"

# Remove all build artifacts (keeps build/.keep)
[unix]
clean:
    find build -mindepth 1 ! -name .keep -exec rm -rf {} +

# Remove all build artifacts (keeps build/.keep)
[windows]
clean:
    Get-ChildItem build -Force -Exclude .keep | Remove-Item -Recurse -Force
