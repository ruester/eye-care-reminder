# Eye Care Reminder build recipes.
# Release artifacts are written to build/ (created on demand, ignored by git).

set windows-shell := ["pwsh", "-NoLogo", "-NoProfile", "-Command"]

# Latest published release. After a tag vX.Y.Z is released, CI runs
# `just bump-version X.Y.Z` and commits it together with the download links in
# README.md and site/index.html.
release_version := "0.1.5"

# Version stamped into builds, e.g. VERSION=1.2.3 just build-linux. MSI requires x.y.z.
version := env("VERSION", "0.0.0")

linux_bin := "build/eye-care-reminder-" + version + "-linux.bin"
windows_msi := "build/eye-care-reminder-" + version + "-windows-x64.msi"

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

# Build the Windows tray app and MSI installer (requires the .NET SDK and WiX Toolset, see CLAUDE.md)
[windows]
build-windows:
    if (Test-Path build/windows) { Remove-Item -Recurse -Force build/windows }
    dotnet publish src/windows/app/EyeCareReminder.csproj -c Release -o build/windows/payload -p:Version={{version}}
    wix build src/windows/installer/Package.wxs -arch x64 -ext WixToolset.Util.wixext -ext WixToolset.UI.wixext -d Version={{version}} -bindpath payload=build/windows/payload -o {{windows_msi}}
    Write-Host "Built {{windows_msi}} (version {{version}})"

# Run the Windows unit tests with line coverage (report in build/test-results)
[windows]
test-windows:
    if (Test-Path build/test-results) { Remove-Item -Recurse -Force build/test-results }
    dotnet test src/windows/tests/EyeCareReminder.Tests.csproj -c Debug --collect "Code Coverage" --settings src/windows/tests/coverage.runsettings --results-directory build/test-results
    ./src/windows/tests/Get-Coverage.ps1 -ResultsDir build/test-results

# Set release_version and the download links in README.md and site/index.html
# (run by CI after a release; never downgrades)
[unix]
bump-version new_version:
    #!/usr/bin/env bash
    set -euo pipefail
    new="{{new_version}}"
    [[ "$new" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "Version must be major.minor.patch, e.g. 1.0.0" >&2; exit 1; }
    old="{{release_version}}"
    if [[ "$old" == "$new" ]]; then echo "Release version is already $new"; exit 0; fi
    if [[ "$(printf '%s\n' "$old" "$new" | sort -V | tail -n 1)" != "$new" ]]; then
        echo "Keeping release version $old: $new is older"; exit 0
    fi
    old_re="${old//./\\.}"
    sed -i.bak -E "s/^release_version := \"$old_re\"/release_version := \"$new\"/" justfile
    for file in README.md site/index.html; do
        sed -i.bak -E -e "s#/download/v$old_re/#/download/v$new/#g" -e "s/eye-care-reminder-$old_re-/eye-care-reminder-$new-/g" -e "s/([Vv]ersion )$old_re/\\1$new/g" "$file"
    done
    rm -f justfile.bak README.md.bak site/index.html.bak
    echo "Release version $old -> $new"

# Remove all build artifacts
[unix]
clean:
    rm -rf build

# Remove all build artifacts
[windows]
clean:
    if (Test-Path build) { Remove-Item -Recurse -Force build }
