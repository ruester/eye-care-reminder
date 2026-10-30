# Eye Care Reminder

[![Build](https://github.com/ruester/eye-care-reminder/actions/workflows/build.yml/badge.svg)](https://github.com/ruester/eye-care-reminder/actions/workflows/build.yml)
[![Latest release](https://img.shields.io/github/v/release/ruester/eye-care-reminder?sort=semver)](https://github.com/ruester/eye-care-reminder/releases/latest)

Eye Care Reminder is a lightweight desktop application for Windows and Linux that helps reduce eye strain during long periods of screen work. At a user-defined interval, it displays a desktop notification reminding you to look away from the screen and give your eyes a rest.

**Downloads (latest release):**
[Linux installer (.bin)](https://github.com/ruester/eye-care-reminder/releases/latest/download/eye-care-reminder-linux.bin) ·
[Windows installer (.msi)](https://github.com/ruester/eye-care-reminder/releases/latest/download/eye-care-reminder-windows-x64.msi)

## Development

All builds run through [just](https://github.com/casey/just) (`just --list` shows the available recipes). Build output is written to `build/`. To stamp a version into a build, set the `VERSION` environment variable (numeric `major.minor.patch`, default `0.0.0`), e.g. `VERSION=1.2.3 just build-linux` or, in PowerShell, `$env:VERSION = "1.2.3"; just build-windows`.

### Windows

Requirements:

- Windows 10 (1903 or later) or Windows 11
- [just](https://github.com/casey/just)
- [PowerShell 7](https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-windows) (`pwsh`)
- [.NET SDK](https://dotnet.microsoft.com/download) 8.0 or later (builds the .NET Framework 4.8 app)
- [WiX Toolset](https://wixtoolset.org/) 5.0.2 with the Util and UI extensions

Install them with:

```powershell
winget install Casey.Just Microsoft.PowerShell Microsoft.DotNet.SDK.8
dotnet tool install --global wix --version 5.0.2
wix extension add --global WixToolset.Util.wixext/5.0.2
wix extension add --global WixToolset.UI.wixext/5.0.2
```

Build the installer (`build/eye-care-reminder-windows-x64.msi`):

```powershell
just build-windows
```

### Linux

Requirements:

- [just](https://github.com/casey/just)
- `bash`, `tar`, `gzip` and `awk` (preinstalled on most distributions)

Install `just` on Debian/Ubuntu (24.04 or later) with:

```bash
sudo apt install just
```

Build the installer (`build/eye-care-reminder-linux.bin`):

```bash
just build-linux
```
