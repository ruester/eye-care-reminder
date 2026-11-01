# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

Eye Care Reminder is a desktop notification app for **Windows** and **Linux**
that periodically (user-defined interval) reminds the user to rest their eyes.

## Workflow

Work directly on `main`: commit and push there. Do not create feature branches.

## License

MIT (`LICENSE`, copyright holder Matthias Rüster). The README and the website
footer link to it.

## Repository layout

```
src/
  linux/
    installer/     header.sh (self-extracting stub) + install.sh (DE detection/installation)
    freedesktop/   generic variant: freedesktop.org Desktop Notifications (D-Bus)
    xfce/          Xfce variant
    unity/         Unity (Ubuntu) variant
  windows/
    app/           C# WinForms tray app (.NET Framework 4.8, EyeCareReminder.csproj)
    installer/     Package.wxs (WiX Toolset v5 source for the MSI), l10n/*.wxl (installer texts),
                   Build-Msi.ps1 (multilingual MSI build), Test-Installer.ps1
    tests/         xunit unit tests for the app's helpers (EyeCareReminder.Tests.csproj)
site/              landing page (static HTML/CSS/JS, i18n.js translations), deployed to GitHub Pages
build/             build output; created by the just recipes, not tracked
justfile           all build recipes
.github/workflows/build.yml   CI + GitHub release publishing + download link update
.github/workflows/pages.yml   website deployment (GitHub Pages)
```

New Linux desktop environments get their own folder under `src/linux/<name>/`
and must be added to `SUPPORTED`, the detection logic and the prompt in
`src/linux/installer/install.sh`, and to the `cp` line in `build-linux`.

## Building

All builds go through `just` (`just --list` shows the recipes):

- `just build-linux` -> `build/eye-care-reminder-<version>-linux.bin` (Linux/macOS host)
- `just build-windows` -> `build/eye-care-reminder-<version>-windows-x64.msi` (Windows host
  with the .NET SDK and `pwsh`; install WiX once with
  `dotnet tool install --global wix --version 5.0.2` and
  `wix extension add --global WixToolset.Util.wixext/5.0.2` and
  `wix extension add --global WixToolset.UI.wixext/5.0.2`)
- `just test-windows` -> runs the Windows unit tests with line coverage
  (Cobertura report in `build/test-results`, Windows host with the .NET SDK)
- `just clean` -> deletes `build/`

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

## Windows app

- `src/windows/app` is a WinForms app without a main window, targeting
  **.NET Framework 4.8** (preinstalled on Windows 10 1903+ / 11, so the MSI
  needs no runtime). Keep it dependency-free (no NuGet packages).
- `TrayApplicationContext` owns the tray icon (left click or "Settings..."
  opens `SettingsForm`, which also has a "Test notification" button; menu also
  has "Take a break now" and "Exit") and a
  timer that shows a notification every interval. Unlocking the session
  restarts the interval.
- Notifications are drawn by the app itself (`NotificationPopup`: borderless,
  topmost, non-activating window in the bottom-right corner of the primary
  screen's work area, closes on click; with auto-hide enabled it also closes
  after the configured time and a countdown bar at the bottom shrinks from
  right to left until it closes). Do not switch back to
  `NotifyIcon.ShowBalloonTip`: Windows 10/11 silently drops those when Do Not
  Disturb / Focus Assist is on or app notifications are disabled.
- Startup: the logon autostart entry passes `--autostart` and the app starts
  silently in the tray. Any other launch (Start menu, installer's "Launch"
  checkbox) opens the settings dialog so the user sees that the app is running
  (Windows 11 hides new tray icons in the overflow by default).
- Settings (under `HKCU\Software\EyeCareReminder`, see `Settings.cs`), DWORDs
  `IntervalMinutes` (default 60, range 1-1440), `AutoHide` (0/1, default 1)
  and `AutoHideSeconds` (default 60, range 1-300), and the string `Language`
  (also written by the installer). "Test notification" uses the auto-hide
  values and the language currently selected in the dialog, even if unsaved.

## Languages (Windows app and installer)

- Supported: English (`en`, no US/GB distinction, UK flag), German `de`,
  French `fr`, Italian `it`, Spanish `es`, Portuguese `pt`, Dutch `nl`,
  Norwegian Bokmål `nb`, Swedish `sv`, Finnish `fi`, Czech `cs`, Polish `pl`,
  Croatian `hr`, plus Belgium as `nl-BE` and `fr-BE` (same texts as nl/fr, Belgian
  flag). The switcher lists native country names ("Deutschland", "België",
  "Belgique", ..., "English") with flags.
- App: `Language.cs` (`Languages.All`, detection, codes), `Translations.cs` (all
  texts, `Texts.cs` describes them), `Plural.cs` (one/few/other forms for
  cs/pl/hr), `Flag.cs` + `FlagPainter.cs` (flags drawn with GDI+: Windows has no
  flag emoji), `LanguageComboBox.cs` (owner-drawn switcher in the settings dialog,
  which re-translates itself on change). Language: stored `Language` value if
  valid, else the Windows display language (`CurrentUICulture`; nl/fr become
  Belgian if the UI or regional format culture is `-BE`; nn/no -> nb), else English.
- Adding a text: add a property to `Texts` and a value in every language of
  `Translations` (the unit tests check completeness, placeholders and `&`
  accelerators). Adding a language: `Translations`, `Languages.All`, `Flags`,
  the installer's `ComboBox` list in `Package.wxs`, and (for installer texts) a
  culture in `Build-Msi.ps1` plus `l10n/<culture>.wxl`.
- Installer: `Build-Msi.ps1` builds `Package.wxs` once per culture (13 cultures,
  `l10n/<culture>.wxl` + the WixUI translations), derives a code-page-neutral base
  (code page 0, ASCII country names) from the en-US MSI because a transform can't
  change a fixed code page, creates language transforms
  (`wix msi transform -t language`) from that base to every culture (en-US too), embeds them as
  substorages named by LCID and lists all LCIDs in the summary Template, then
  checks each transform. Windows Installer applies the transform of the Windows
  display language automatically (`TRANSFORMS=:1029` forces one). The wizard
  language itself can't be switched at runtime (MSI limitation); the extra
  `LanguageDlg` page (after Welcome) chooses the app language (`APPLANGUAGE`,
  default: the transform's language, Belgian via `UserLanguageID`, or the
  previously installed value) and writes it to HKCU. Code pages: 1252, and 1250
  for cs/pl/hr, so the MSI list shows "Cesko" resp. "Espana" where Č/ñ don't
  fit the code page (`NameCzechia`/`NameSpain` strings).
- Single instance via a named mutex; launching the exe again signals the running
  instance (named event) to open the settings dialog.
- `NotifyIcon.Text` must stay <= 63 characters (throws otherwise on .NET Framework).
- `EyeCareReminder.ico` uses BMP frames up to 64px and a PNG frame for 256px;
  keep it that way (PNG-only frames break some icon loaders).

## Windows unit tests

- `src/windows/tests` tests the app's helpers, not the UI: `TimeFormat`
  (interval texts, tray tooltip <= 63 chars), `Countdown` (popup countdown
  bar), `Settings` (defaults, ranges, round trip) and
  `Program.ShouldOpenSettings`. Put new logic into such UI-free helpers so it
  can be tested; the app exposes internals via `InternalsVisibleTo`.
- The test project may use NuGet packages (xunit, Microsoft.NET.Test.Sdk);
  the app itself stays dependency-free.
- `SettingsTests` sets `Settings.KeyPath` to a throwaway key below
  `HKCU\Software\EyeCareReminder.Tests` and deletes it afterwards.
- Coverage uses Microsoft Code Coverage (`coverage.runsettings`, limited to
  `EyeCareReminder.exe`), so it is measured over the whole app including UI code.
  Tests run in Debug because Release builds have no PDBs.
- Coverage badge: on pushes to `main` the CI Windows job renders
  `windows-coverage.svg` and force-pushes it as the only commit of the
  CI-managed `badges` branch (do not delete it or work on it). The Linux
  coverage badge in the README is static (`n/a`) until there is Linux code.

## Windows installer notes

- The MSI installs to `Program Files\Eye Care Reminder`, adds a Start menu
  shortcut, registers autostart for all users
  (`HKLM\...\CurrentVersion\Run`).
- Running app on install/upgrade/uninstall: the deferred `CloseTrayApp` action
  (`WixQuietExec` + `taskkill /F`, LocalSystem) ends every instance right after
  `InstallInitialize`, before files are touched. `MajorUpgrade` uses
  `Schedule="afterInstallExecute"` (new files first, old product removed last):
  `RemoveExistingProducts` may not follow script-generating actions such as
  `CloseTrayApp` when scheduled early (error 2613). `MSIRESTARTMANAGERCONTROL=Disable`
  avoids the "files in use" prompt.
- CI tests this with `src/windows/installer/Test-Installer.ps1`: installs a
  0.0.0 build with the Czech transform (checks product language 1029 and app
  language `cs`), starts the app, upgrades to the current build (language must be
  kept) and uninstalls, each while the app is running (no reboot, no leftovers,
  one product entry).
  Non-tag CI builds are versioned `0.0.<run number>` so the upgrade is real.
- Setup wizard: `WixUI_InstallDir` plus `LanguageDlg`, with the license page skipped (no license
  yet; drop the two `Order="99"` overrides once a `WixUILicenseRtf` exists).
  The final page has a "Launch Eye Care Reminder" checkbox (`WixShellExec`,
  runs as the non-elevated user). Silent installs (`/qn`) don't launch the app;
  it starts at the next logon.

- The MSI is built with the WiX Toolset and is **not code-signed**. This is
  valid: the MSI installs normally, but Windows SmartScreen shows
  "Windows protected your PC" for downloaded files; users must click
  "More info" -> "Run anyway". Signing would require a code-signing
  certificate (e.g. Azure Trusted Signing, OV/EV certificate) and can be added
  later as a `signtool` step after `wix build`.
- Keep `UpgradeCode` in `Package.wxs` unchanged forever; it links versions for
  major upgrades.

## Website

- `site/` is a static landing page (no build step, no framework):
  `index.html`, `style.css`, `logo.svg` (vector copy of the app
  icon) and PNG icons. Its colours match the Windows app (`#00897B` accent,
  `#26A69A`, `#D6ECE9` countdown track, `#142128`); it supports dark mode.
- Languages: English (in the HTML itself), Spanish, French, Italian and German
  in `i18n.js` (elements with `data-i18n` keys; `{version}` = `<html data-version>`).
  Selection: `?lang=xx`, else the choice remembered in localStorage, else the
  browser language. Translate new texts in all four languages there.
- The download buttons link directly to the `.msi` of `release_version`
  (updated by CI after each release, see Releases). Keep the page truthful: Linux is shown as "in development"
  until the Linux app exists.
- `.github/workflows/pages.yml` deploys `site/` on pushes to `main` that touch
  it. It is skipped while the repository is private (Pages needs a paid plan
  for private repos). After making the repo public, set Settings -> Pages ->
  Source to "GitHub Actions" and run the workflow once; the site is then at
  https://ruester.github.io/eye-care-reminder/.
- `build.yml` ignores changes that only touch the site.

## Releases

`.github/workflows/build.yml` runs the Windows unit tests and builds both installers on every push to any branch and on PRs. Pushing a
tag `vX.Y.Z` additionally creates a GitHub release with both installers
attached. Asset names contain the version
(`eye-care-reminder-<version>-linux.bin`, `eye-care-reminder-<version>-windows-x64.msi`)
so repeated downloads don't overwrite each other.

`release_version` in the justfile is the latest published release. The README
and `site/index.html` link directly to that release's installers
(`releases/download/vX.Y.Z/...`) and show its version. Don't edit these by
hand: after publishing a tag's release, the `update-download-links` job in
`build.yml` runs `just bump-version X.Y.Z` on main (never downgrades, no-op if
already current), commits "Update download links to vX.Y.Z" and, if the repo
is public, starts the website deployment (pushes with `GITHUB_TOKEN` don't
trigger workflows, a `workflow_dispatch` does). The links therefore only
switch once the new installers exist. Pull afterwards: main has that commit.

Release by tagging main:

```bash
git pull && git tag v1.0.0 && git push origin v1.0.0
```
