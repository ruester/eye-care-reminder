# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

Eye Care Reminder is a desktop notification app for **Windows** and **Linux**
that periodically (user-defined interval) reminds the user to rest their eyes.

## Repository layout

```
src/
  linux/
    installer/     header.sh (self-extracting stub) + install.sh (DE detection/installation)
    freedesktop/   generic variant: freedesktop.org Desktop Notifications (D-Bus)
    xfce/          Xfce variant
    unity/         Unity (Ubuntu) variant
  windows/
    app/           Windows application files (packaged into the MSI)
    installer/     Package.wxs (WiX Toolset v5 source for the MSI)
build/             build output; only build/.keep is tracked
justfile           all build recipes
.github/workflows/build.yml   CI + GitHub release publishing
```

New Linux desktop environments get their own folder under `src/linux/<name>/`
and must be added to `SUPPORTED`, the detection logic and the prompt in
`src/linux/installer/install.sh`, and to the `cp` line in `build-linux`.

## Building

All builds go through `just` (`just --list` shows the recipes):

- `just build-linux` -> `build/eye-care-reminder-linux.bin` (Linux/macOS host)
- `just build-windows` -> `build/eye-care-reminder-windows-x64.msi` (Windows host,
  needs `dotnet tool install --global wix --version 5.0.2`; runs under `pwsh`)
- `just clean` -> empties `build/` except `.keep`

The version comes from the `VERSION` environment variable (default `0.0.0`).
It must be numeric `major.minor.patch` because MSI versions do not allow
suffixes such as `-rc1`.

## Linux notes

- The standard Linux notification mechanism is the freedesktop.org
  **Desktop Notifications Specification** (D-Bus service
  `org.freedesktop.Notifications`), usually used through `libnotify` /
  `notify-send`. Both Xfce (`xfce4-notifyd`) and Unity (`notify-osd`)
  implement it, so the `freedesktop` variant is the fallback for every other DE.
- The `.bin` is a POSIX `sh` header with a gzipped tarball appended after the
  `__PAYLOAD_BELOW__` marker. Keep `header.sh` and `install.sh` POSIX `sh`
  (no bashisms) so they run on Debian/Ubuntu `dash`.
- `install.sh` detects Xfce/Unity by installed binaries/session files. If
  exactly one is found it is used; if both or none are found the user is
  asked (reading from `/dev/tty`, suggesting `$XDG_CURRENT_DESKTOP`).
  `--de=` and `--prefix=` allow non-interactive installs.

## Windows notes

- The MSI is built with the WiX Toolset and is **not code-signed**. This is
  valid: the MSI installs normally, but Windows SmartScreen shows
  "Windows protected your PC" for downloaded files; users must click
  "More info" -> "Run anyway". Signing would require a code-signing
  certificate (e.g. Azure Trusted Signing, OV/EV certificate) and can be added
  later as a `signtool` step after `wix build`.
- Keep `UpgradeCode` in `Package.wxs` unchanged forever; it links versions for
  major upgrades.

## Releases

`.github/workflows/build.yml` builds both installers on every push/PR. Pushing a
tag `vX.Y.Z` additionally creates a GitHub release with both installers
attached. Asset names are version-independent so the README can link to
`releases/latest/download/<asset>`; do not rename them without updating the
README.

```bash
git tag v1.0.0 && git push origin v1.0.0
```
