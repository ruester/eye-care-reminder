# Eye Care Reminder

[![Build](https://github.com/ruester/eye-care-reminder/actions/workflows/build.yml/badge.svg)](https://github.com/ruester/eye-care-reminder/actions/workflows/build.yml)
[![Releases](https://img.shields.io/badge/Releases-Download-blue)](https://github.com/ruester/eye-care-reminder/releases/latest)
[![Windows unit test coverage](.github/badges/windows-coverage.svg)](https://github.com/ruester/eye-care-reminder/actions/workflows/build.yml)
[![Linux unit test coverage](.github/badges/linux-coverage.svg)](https://github.com/ruester/eye-care-reminder/actions/workflows/build.yml)

Eye Care Reminder is a lightweight desktop application for Windows and Linux that helps reduce eye strain during long periods of screen work. At a user-defined interval, it displays a desktop notification reminding you to look away from the screen and give your eyes a rest.

The app is available in English, German, French, Italian, Spanish, Portuguese, Dutch, Norwegian, Swedish, Finnish, Czech, Polish and Croatian. It starts in the language of your system (Windows display language, or the locale on Linux); the settings dialog and the Windows installer have a language switcher.

**Downloads:** [Windows installer (.msi)](https://github.com/ruester/eye-care-reminder/releases/download/v1.1.0/eye-care-reminder-1.1.0-windows-x64.msi) · [Linux installer (.bin)](https://github.com/ruester/eye-care-reminder/releases/download/v1.1.0/eye-care-reminder-1.1.0-linux.bin) · [all releases](https://github.com/ruester/eye-care-reminder/releases)

## Installation

### Windows

Download the `.msi` and double-click it. The installer isn't code-signed, so Microsoft Defender SmartScreen may warn about it: click *More info* and then *Run anyway*. To uninstall, go to *Settings → Apps → Installed apps*.

### Linux

The Linux app is made for **Xfce**. It also runs on other desktops (GNOME, KDE Plasma, Cinnamon, MATE, ...); whether its tray icon appears there depends on the desktop's tray icon support (AppIndicator), but the reminders work everywhere and the settings are always in the application menu.

Download the `.bin`, make it executable and run it in a terminal (no `sudo` needed):

```bash
chmod +x eye-care-reminder-1.1.0-linux.bin
```

```bash
./eye-care-reminder-1.1.0-linux.bin
```

(Without `chmod`, `sh eye-care-reminder-1.1.0-linux.bin` works too.) The installer

- first checks the system: Linux, desktop (Xfce is supported; others work with limitations, it asks before installing there), display server, Python 3.8+ and the GTK 3 dependencies. `--check` runs only this check,
- installs the app for your user to `~/.local/share/eye-care-reminder`, with an application menu entry and an autostart entry, and starts it,
- needs Python 3 with GTK 3 (PyGObject). Most desktop distributions have it preinstalled; otherwise the installer lists what is missing, shows the command for your package manager (apt, dnf, zypper or pacman, e.g. `sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0`) and offers to run it,
- upgrades an installed version in place (settings in `~/.config/eye-care-reminder` are kept).

Run it with `sudo` to install for all users instead (`/opt/eye-care-reminder`, autostart in `/etc/xdg/autostart`). `--help` lists the options (`--check`, `--no-launch`, `--uninstall`).

To uninstall:

```bash
sh ~/.local/share/eye-care-reminder/uninstall.sh
```

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

Build the installer (`build/eye-care-reminder-<version>-windows-x64.msi`, one MSI with embedded language transforms):

```powershell
just build-windows
```

Run the unit tests with line coverage (report in `build/test-results`):

```powershell
just test-windows
```

### Linux

The Linux app (`src/linux/app`) is written in Python 3 with GTK 3 (PyGObject); the installer is a self-extracting POSIX shell script.

Requirements:

- [just](https://github.com/casey/just)
- `bash`, `tar`, `gzip` and `awk` (preinstalled on most distributions)
- to run and test the app: Python 3.8 or later with PyGObject (GTK 3) and pycairo, optionally coverage.py

Install them on Debian/Ubuntu (24.04 or later) with:

```bash
sudo apt install just python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-coverage
```

Build the installer (`build/eye-care-reminder-<version>-linux.bin`):

```bash
just build-linux
```

Run the unit tests with line coverage (report in `build/linux-test-results`):

```bash
just test-linux
```

Run the app from the source tree:

```bash
python3 src/linux/app/eye-care-reminder.py
```

## License

Eye Care Reminder is released under the [MIT License](LICENSE).
