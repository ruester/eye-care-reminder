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
    app/           Python 3 + GTK 3 tray app (eye-care-reminder.py + eye_care_reminder/ package, icons/)
    installer/     header.sh (self-extracting stub), install.sh (install/upgrade/uninstall),
                   eye-care-reminder.desktop.in (menu + autostart entry)
    tests/         unittest tests (test_*.py) and test-installer.sh (end-to-end, CI)
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
.github/badges/               coverage badges, committed by CI
.github/scripts/              publish-coverage-badge.sh (used by build.yml)
```

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
- `just test-linux` -> runs the Linux unit tests, with line coverage if coverage.py
  is installed (`build/linux-test-results`; `PYTHON=` picks the interpreter)
- `just clean` -> deletes `build/`

The version comes from the `VERSION` environment variable (default `0.0.0`).
It must be numeric `major.minor.patch` because MSI versions do not allow
suffixes such as `-rc1`.

## Linux app

- Supported desktops: **Xfce**, **Ubuntu Unity**, **GNOME**, **KDE Plasma**, **i3**. The
  same app is installed on every desktop; there is no per-desktop variant (`desktop.py`
  detects the desktop at runtime). Python 3.8+ with PyGObject (GTK 3) and pycairo only, no
  pip packages (Debian/Ubuntu: `python3-gi python3-gi-cairo gir1.2-gtk-3.0`), plus
  AyatanaAppIndicator3/AppIndicator3 on Unity/GNOME/KDE (`gir1.2-ayatanaappindicator3-0.1`)
  and on GNOME the shell extension "AppIndicator and KStatusNotifierItem Support"
  (`gnome-shell-extension-appindicator`, built into Ubuntu).
- It mirrors the Windows app (same features, texts, languages, settings ranges):
  - `eye_care_reminder/` modules without GTK (unit tested): `plural`, `translations`
    (same texts as `Translations.cs`; a test compares them, so change both), `languages`
    (list as in `Language.cs`; detection from `LC_ALL`/`LC_MESSAGES`/`LANG`/`LANGUAGE`,
    Belgian via the messages or `LC_TIME` locale), `flags` + `painting` (cairo: flags,
    app icon; `python3 -m eye_care_reminder.painting DIR` re-renders `icons/*.png`),
    `settings` (`$XDG_CONFIG_HOME/eye-care-reminder/settings.ini`, keys
    `interval_minutes`, `auto_hide`, `auto_hide_seconds`, `language`), `timeformat`,
    `countdown`, `main` (`--version`), `desktop` (detection from `XDG_CURRENT_DESKTOP`,
    i3 also via `I3SOCK` without `SWAYSOCK`; Budgie/Flashback/Pantheon aren't GNOME Shell;
    tray kind; i3 work area from `i3-msg -t get_workspaces`, since i3 has no
    `_NET_WORKAREA`), `fallback` (fallback commands and notification daemons to start).
  - GTK modules: `app` (Gtk.Application `io.github.ruester.EyeCareReminder`: single
    instance per session, a second start opens the settings unless `--autostart`; a
    wall-clock check every 5 s shows the reminder, so suspend doesn't delay it),
    `ui_tray` (Gtk.StatusIcon on Xfce and i3: left click = settings, tooltip = next break;
    AppIndicator elsewhere if installed, icon by name with the app's `icons/` as theme
    path (SVG); next break as a menu entry; warns on stderr on GNOME without a
    StatusNotifierWatcher), `ui_popup` (own popup on X11 like Windows:
    override-redirect window bottom right of the work area (on i3 above i3bar), countdown
    bar, no focus, ignores Do Not Disturb, needs no window manager. If not possible (pure
    Wayland) or failing, `FallbackReminder` tries in order: notification daemon over
    D-Bus (if running or activatable), starting an installed mako (Wayland) / dunst,
    `notify-send`, `kdialog --passivepopup`, an ordinary app window (`managed=True`),
    `xmessage`; a command counts as shown if it exits 0 or still runs after 3 s; each
    failure is logged to stderr), `ui_settings` (dialog with flag language switcher),
    `session_lock` (unlock / screen saver end restarts the interval:
    org.freedesktop/xfce/gnome/cinnamon/mate ScreenSaver `ActiveChanged`, Unity's
    `com.canonical.Unity.Session` `Unlocked`, logind `Unlock` and `LockedHint`).
  - Under Wayland the app runs through XWayland (`GDK_BACKEND=x11`) if available.
- Installer (`.bin`): POSIX `sh` header with a gzipped tarball (`installer/`, `app/`,
  `VERSION`) after the `__PAYLOAD_BELOW__` marker. Keep `header.sh` and `install.sh`
  POSIX `sh` (no bashisms; Debian's `dash`), checked with shellcheck in CI. `install.sh`:
  - as a user: `~/.local/share/eye-care-reminder`, launcher `~/.local/bin/eye-care-reminder`
    (runs the app with the python3 that has GTK, preferring `/usr/bin/python3`), menu entry
    in `~/.local/share/applications`, icons in `~/.local/share/icons/hicolor`, autostart
    in `~/.config/autostart` (`--autostart`); as root: `/opt`, `/usr/local/...`,
    `/etc/xdg/autostart`;
  - compatibility check first (`check_system`, also `--check` alone): Linux, desktop
    (`detect_desktop`: Xfce, Unity, GNOME, KDE Plasma, i3 ok; other desktops: note +
    confirmation on a terminal), display server, Python >= 3.8 and the modules
    gi/gtk/cairo (one probe script; AppIndicator required on Unity/GNOME/KDE, optional
    elsewhere; GNOME: the AppIndicator extension is a dependency, enabled after the
    install with `gnome-extensions enable`; i3: reports whether the i3 config runs `dex`). Incompatible (not Linux, old Python): abort. Missing
    dependencies: lists them, prints the package manager command (apt/dnf/zypper/pacman,
    only the missing packages) and offers to run it (asks on `/dev/tty`; without a
    terminal it aborts). `EYE_CARE_REMINDER_PYTHON` overrides the interpreter (tests);
    `header.sh` checks awk/tail/tar/gzip/mktemp before extracting;
  - upgrade: stops running instances, replaces the files, restarts the app silently if it
    was running; a fresh install starts it with the settings dialog (not as root,
    not with `--no-launch`);
  - i3 without `dex` in the user's i3 config: appends a marker comment and
    `exec --no-startup-id "<launcher>" --autostart` (once); uninstall removes both lines;
    root installs / system configs only print the line;
  - uninstall: `<app dir>/uninstall.sh` (a copy of install.sh) or `--uninstall`; keeps
    the settings file.
- CI runs `src/linux/tests/test-installer.sh` under `xvfb-run dbus-run-session`: checks
  `--check` and the rejection of fake old / incomplete Pythons, the desktop rules (Unity,
  KDE, GNOME extension, Budgie, i3 via `I3SOCK`), installs a
  0.0.0 build, checks files, running app and settings window (xdotool), single instance,
  upgrades while running (settings kept, restarted), uninstalls while running (no
  leftovers), the i3 config autostart line (added once, removed on uninstall, not with
  dex), and installs/uninstalls as root.

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
  `IntervalMinutes` (default 20 (20-20-20 rule), range 1-1440), `AutoHide` (0/1, default 1)
  and `AutoHideSeconds` (default 60, range 1-300), and the string `Language`
  (also written by the installer). "Test notification" uses the auto-hide
  values and the language currently selected in the dialog, even if unsaved.

## Languages (Windows app and installer; the Linux app has the same languages and texts)

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
- Coverage badges: on pushes to `main` the CI Windows and Linux jobs render
  `.github/badges/{windows,linux}-coverage.svg` (shields.io, via
  `.github/scripts/publish-coverage-badge.sh`) and commit them to `main`
  ("Update Windows coverage badge to N%") when they changed; the README shows them via
  relative paths. Don't edit them by hand. Linux coverage is measured over the whole
  `src/linux/app` (GTK modules included, they are only tested end-to-end).

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
  0.0.0 build with the Czech transform (`TRANSFORMS=:1029`, checks app
  language `cs`; the uninstall entry always shows the base language 1033), starts the app, upgrades to the current build (language must be
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
- The download buttons link directly to the `.msi` / `.bin` of `release_version`
  (updated by CI after each release, see Releases); the Linux card shows the
  `chmod +x` / run commands with the versioned file name (also updated by `bump-version`).
- `.github/workflows/pages.yml` deploys `site/` on pushes to `main` that touch
  it. It is skipped while the repository is private (Pages needs a paid plan
  for private repos). After making the repo public, set Settings -> Pages ->
  Source to "GitHub Actions" and run the workflow once; the site is then at
  https://ruester.github.io/eye-care-reminder/.
- `build.yml` ignores changes that only touch the site.

## Releases

`.github/workflows/build.yml` runs the Windows and Linux unit tests, builds both installers and tests them on every push to any branch and on PRs. Pushing a
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

Release by tagging main with an annotated tag whose message summarizes the
release for users (always include a message when proposing tag commands):

```bash
git pull && git tag -a v1.0.0 -m "Short summary of what's new" && git push origin v1.0.0
```
