#!/bin/sh
# Eye Care Reminder - Linux installer (run by the self-extracting .bin, see header.sh).
#
# Installs the app (Python 3 + GTK 3, the same for every desktop environment;
# supported: Xfce and Ubuntu Unity) with a menu entry and an autostart entry:
#   - as a normal user: for this user only (~/.local/share/eye-care-reminder),
#   - as root: for all users (/opt/eye-care-reminder).
# Running a newer .bin upgrades in place. The installed copy of this script,
# <app dir>/uninstall.sh, removes the app again (same as --uninstall).
set -eu

APP=eye-care-reminder
PAYLOAD_DIR=$(cd "$(dirname "$0")/.." && pwd)

usage() {
    cat <<USAGE
Usage: $APP-<version>-linux.bin [--check] [--no-launch] [--uninstall]

Installs Eye Care Reminder for the current user, or for all users when run as root.
Checks the system for compatibility and missing dependencies first.

  --check        Only check the system, don't install anything.
  --no-launch    Don't start the app after installing (it starts at the next login).
  --uninstall    Remove Eye Care Reminder (settings in ~/.config/$APP are kept).
  -h, --help     Show this help.
USAGE
}

say() { printf '%s\n' "$*"; }
fail() { printf 'error: %s\n' "$*" >&2; exit 1; }

action=install
launch=yes
case "$(basename "$0")" in
    uninstall.sh) action=uninstall ;;
esac
for arg in "$@"; do
    case "$arg" in
        --check) action=check ;;
        --no-launch) launch=no ;;
        --uninstall) action=uninstall ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'error: unknown argument: %s\n' "$arg" >&2; usage >&2; exit 1 ;;
    esac
done

if [ "$(id -u)" -eq 0 ]; then
    scope="all users"
    app_dir=/opt/$APP
    bin_dir=/usr/local/bin
    applications_dir=/usr/local/share/applications
    icons_dir=/usr/local/share/icons/hicolor
    autostart_dir=/etc/xdg/autostart
else
    scope="the current user"
    [ -n "${HOME:-}" ] || fail "HOME is not set."
    data_home=${XDG_DATA_HOME:-$HOME/.local/share}
    app_dir=$data_home/$APP
    bin_dir=$HOME/.local/bin
    applications_dir=$data_home/applications
    icons_dir=$data_home/icons/hicolor
    autostart_dir=${XDG_CONFIG_HOME:-$HOME/.config}/autostart
fi
launcher=$bin_dir/$APP
icon_sizes="16 22 24 32 48 64 128 256"

# Ends running instances of the installed app. Prints "yes" if one was running.
stop_app() {
    if command -v pgrep >/dev/null 2>&1 && pgrep -f "$app_dir/$APP.py" >/dev/null 2>&1; then
        pkill -f "$app_dir/$APP.py" >/dev/null 2>&1 || true
        sleep 1
        echo yes
    else
        echo no
    fi
}

# The icon cache must be refreshed if one exists, otherwise new icons stay invisible.
update_icon_cache() {
    if [ -f "$icons_dir/icon-theme.cache" ] && command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f "$icons_dir" >/dev/null 2>&1 || true
    fi
}

remove_files() {
    rm -rf "$app_dir"
    rm -f "$launcher" "$applications_dir/$APP.desktop" "$autostart_dir/$APP.desktop"
    for size in $icon_sizes; do
        rm -f "$icons_dir/${size}x$size/apps/$APP.png"
    done
    rm -f "$icons_dir/scalable/apps/$APP.svg"
    update_icon_cache
}

if [ "$action" = uninstall ]; then
    [ -d "$app_dir" ] || [ -e "$launcher" ] || fail "Eye Care Reminder is not installed for $scope ($app_dir)."
    stop_app >/dev/null
    remove_files
    say "Eye Care Reminder has been removed for $scope."
    if [ "$scope" = "the current user" ]; then
        say "Your settings are kept in ${XDG_CONFIG_HOME:-$HOME/.config}/$APP (delete that folder to remove them)."
    fi
    exit 0
fi

# --- Compatibility check (before anything is installed) ---
# Supported: Linux with Python 3.8+, PyGObject, GTK 3 and pycairo on Xfce and on
# Ubuntu Unity (there also AppIndicator: Unity's panel only shows AppIndicators);
# other desktops work with limitations. EYE_CARE_REMINDER_PYTHON overrides the
# Python interpreter (used by the tests).

# Prints the Python version and the available modules, e.g. "3.12 gi gtk cairo indicator".
PROBE='
import sys
found = ["%d.%d" % sys.version_info[:2]]
try:
    import gi
    found.append("gi")
    try:
        gi.require_version("Gtk", "3.0")
        found.append("gtk")
    except ValueError:
        pass
    try:
        gi.require_foreign("cairo")
        found.append("cairo")
    except ImportError:
        pass
    for namespace in ("AyatanaAppIndicator3", "AppIndicator3"):
        try:
            gi.require_version(namespace, "0.1")
            found.append("indicator")
            break
        except ValueError:
            pass
except ImportError:
    pass
print(" ".join(found))
'
REQUIRED_MODULES="gi gtk cairo"
required_modules=$REQUIRED_MODULES  # plus "indicator" on Unity (check_system)

python_candidates() {
    if [ -n "${EYE_CARE_REMINDER_PYTHON:-}" ]; then
        echo "$EYE_CARE_REMINDER_PYTHON"
        return
    fi
    echo /usr/bin/python3
    command -v python3 2>/dev/null || true
}

has_module() { case " $modules " in *" $1 "*) return 0 ;; esac; return 1; }

# Whether the probe result $1 contains every required module.
has_required_modules() {
    for module in $required_modules; do
        case " $1 " in
            *" $module "*) ;;
            *) return 1 ;;
        esac
    done
}

# Sets python, python_version and modules: the first interpreter with all required
# modules, else the first one found (to report what is missing).
find_python() {
    python=""
    python_version=""
    modules=""
    for candidate in $(python_candidates); do
        [ -x "$candidate" ] || continue
        result=$("$candidate" -c "$PROBE" 2>/dev/null) || continue
        case "$result" in
            [0-9]*) ;;
            *) continue ;;
        esac
        if [ -z "$python" ] || has_required_modules "$result"; then
            python=$candidate
            python_version=${result%% *}
            modules=${result#"$python_version"}
        fi
        if has_required_modules "$result"; then
            return
        fi
    done
}

python_version_ok() {
    major=${python_version%%.*}
    minor=${python_version#*.}
    [ "$major" -gt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; }
}

detect_package_manager() {
    for pm in apt-get dnf zypper pacman; do
        if command -v "$pm" >/dev/null 2>&1; then
            echo "$pm"
            return
        fi
    done
}

# Package of a dependency for the package manager.
package_name() {
    case "$1:$2" in
        apt-get:python) echo python3 ;;
        apt-get:gi) echo python3-gi ;;
        apt-get:gtk) echo gir1.2-gtk-3.0 ;;
        apt-get:cairo) echo python3-gi-cairo ;;
        apt-get:indicator) echo gir1.2-ayatanaappindicator3-0.1 ;;
        dnf:python) echo python3 ;;
        dnf:gi) echo python3-gobject ;;
        dnf:gtk) echo gtk3 ;;
        dnf:cairo) echo python3-cairo ;;
        dnf:indicator) echo libayatana-appindicator-gtk3 ;;
        zypper:python) echo python3 ;;
        zypper:gi) echo python3-gobject ;;
        zypper:gtk) echo typelib-1_0-Gtk-3_0 ;;
        zypper:cairo) echo python3-gobject-cairo ;;
        zypper:indicator) echo typelib-1_0-AyatanaAppIndicator3-0_1 ;;
        pacman:python) echo python ;;
        pacman:gi) echo python-gobject ;;
        pacman:gtk) echo gtk3 ;;
        pacman:cairo) echo python-cairo ;;
        pacman:indicator) echo libayatana-appindicator ;;
    esac
}

install_command() {
    case "$1" in
        apt-get) echo "apt-get install -y" ;;
        dnf) echo "dnf install -y" ;;
        zypper) echo "zypper --non-interactive install" ;;
        pacman) echo "pacman -S --needed --noconfirm" ;;
    esac
}

describe() {
    case "$1" in
        python) echo "Python 3" ;;
        gi) echo "PyGObject (GObject introspection for Python)" ;;
        gtk) echo "GTK 3" ;;
        cairo) echo "cairo support for PyGObject (pycairo)" ;;
        indicator) echo "AppIndicator (tray icon outside Xfce)" ;;
        indicator-unity) echo "AppIndicator (tray icon in Unity's panel)" ;;
    esac
}

report() { printf '  %-8s %s\n' "$1" "$2"; }

is_interactive() { (: </dev/tty) 2>/dev/null; }

# Asks a yes/no question on the terminal (default yes); "no" without a terminal.
confirm() {
    is_interactive || return 1
    printf '%s [Y/n] ' "$1" >/dev/tty
    read -r answer </dev/tty || return 1
    case "$answer" in
        ""|y|Y|yes|Yes) return 0 ;;
    esac
    return 1
}

# Checks the system and prints a report. Sets: incompatible (yes/no), missing
# (required dependencies), unsupported_desktop (yes/no).
check_system() {
    incompatible=no
    missing=""
    unsupported_desktop=no
    say "Checking the system for compatibility ..."

    distribution=""
    if [ -r /etc/os-release ]; then
        # shellcheck disable=SC1091
        distribution=$(. /etc/os-release && printf '%s' "${PRETTY_NAME:-${NAME:-}}")
    fi
    if [ "$(uname -s)" = Linux ]; then
        report ok "Linux $(uname -r) ($(uname -m))${distribution:+, $distribution}"
    else
        report error "Linux is required (this is $(uname -s))"
        incompatible=yes
    fi

    desktop=${XDG_CURRENT_DESKTOP:-}
    case "$(printf '%s' "$desktop" | tr '[:upper:]' '[:lower:]')" in
        *xfce*) report ok "Desktop: Xfce" ;;
        unity*|*:unity*)
            report ok "Desktop: Unity"
            required_modules="$REQUIRED_MODULES indicator"
            ;;
        "") report note "No desktop session found (e.g. over SSH): the app starts at the next login" ;;
        *)
            report note "Desktop: $desktop is not officially supported (made for Xfce): the reminders work, the tray icon depends on the desktop"
            unsupported_desktop=yes
            ;;
    esac

    case "${XDG_SESSION_TYPE:-}" in
        x11) report ok "Display: X11" ;;
        wayland)
            if [ -n "${DISPLAY:-}" ]; then
                report ok "Display: Wayland with XWayland"
            else
                report note "Display: Wayland without XWayland: reminders are shown as standard notifications"
            fi
            ;;
    esac

    find_python
    if [ -z "$python" ]; then
        report missing "$(describe python)"
        missing="python $required_modules"
        return
    fi
    if ! python_version_ok; then
        report error "Python 3.8 or later is required (found $python_version: $python)"
        incompatible=yes
        return
    fi
    report ok "Python $python_version ($python)"
    for module in $required_modules; do
        name=$module
        [ "$module" != indicator ] || name=indicator-unity
        if has_module "$module"; then
            report ok "$(describe "$name")"
        else
            report missing "$(describe "$name")"
            missing="$missing $module"
        fi
    done
    if [ "$unsupported_desktop" = yes ]; then
        if has_module indicator; then
            report ok "$(describe indicator)"
        else
            package=$(package_name "$(detect_package_manager)" indicator)
            report note "Optional: $(describe indicator) is not installed${package:+ (package $package)}"
        fi
    fi
}

check_system

if [ "$incompatible" = yes ]; then
    fail "This system is not compatible with Eye Care Reminder."
fi

if [ -n "$missing" ]; then
    pm=$(detect_package_manager)
    packages=""
    for dependency in $missing; do
        packages="$packages $(package_name "$pm" "$dependency")"
    done
    if [ -z "$pm" ]; then
        names=""
        for dependency in $missing; do
            names="$names, $(describe "$dependency")"
        done
        fail "Missing dependencies: ${names#, }. Install them with your package manager, then run this installer again."
    fi
    command="$(install_command "$pm")$packages"
    [ "$(id -u)" -eq 0 ] || command="sudo $command"
    if [ "$action" = check ]; then
        say "Missing dependencies can be installed with: $command"
        exit 1
    fi
    if ! confirm "Install the missing dependencies now with \"$command\"?"; then
        fail "Install the missing dependencies with \"$command\", then run this installer again."
    fi
    sh -c "$command" || fail "Installing the dependencies failed."
    find_python
    { [ -n "$python" ] && has_required_modules "$modules"; } || fail "The dependencies are still missing after the installation."
    say "Dependencies installed."
fi

if [ "$action" = check ]; then
    say "This system is compatible with Eye Care Reminder."
    exit 0
fi

if [ "$unsupported_desktop" = yes ] && is_interactive && ! confirm "Install Eye Care Reminder on $desktop anyway?"; then
    say "Installation cancelled."
    exit 1
fi

# --- Install (upgrades replace the previous version) ---
version=$(cat "$PAYLOAD_DIR/VERSION" 2>/dev/null || echo 0.0.0)
was_running=$(stop_app)
if [ -d "$app_dir" ]; then
    say "Upgrading Eye Care Reminder to version $version for $scope ..."
else
    say "Installing Eye Care Reminder $version for $scope ..."
fi
remove_files
mkdir -p "$app_dir" "$bin_dir" "$applications_dir" "$autostart_dir"
cp -R "$PAYLOAD_DIR/app/." "$app_dir/"
find "$app_dir" -name __pycache__ -prune -exec rm -rf {} +
echo "$version" > "$app_dir/VERSION"
cp "$PAYLOAD_DIR/installer/install.sh" "$app_dir/uninstall.sh"
chmod 755 "$app_dir/$APP.py" "$app_dir/uninstall.sh"

# Launcher: runs the app with the Python that has GTK (not e.g. a virtualenv's python3).
cat > "$launcher" <<LAUNCHER
#!/bin/sh
exec "$python" "$app_dir/$APP.py" "\$@"
LAUNCHER
chmod 755 "$launcher"

for size in $icon_sizes; do
    mkdir -p "$icons_dir/${size}x$size/apps"
    cp "$app_dir/icons/$APP-$size.png" "$icons_dir/${size}x$size/apps/$APP.png"
done
mkdir -p "$icons_dir/scalable/apps"
cp "$app_dir/icons/$APP.svg" "$icons_dir/scalable/apps/$APP.svg"
update_icon_cache

# Menu entry (opens the settings) and login autostart entry (starts silently in the tray).
desktop_entry() {
    sed -e "s|@EXEC@|\"$launcher\"$1|" "$PAYLOAD_DIR/installer/$APP.desktop.in"
}
desktop_entry "" > "$applications_dir/$APP.desktop"
desktop_entry " --autostart" > "$autostart_dir/$APP.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q "$applications_dir" >/dev/null 2>&1 || true
fi

say "Installed to $app_dir."
say "Eye Care Reminder starts automatically when you log in; it is also in the application menu."
say "To uninstall, run: sh \"$app_dir/uninstall.sh\""

# Start it now (like the Windows installer's "Launch" checkbox): a fresh install
# opens the settings, an upgrade restarts a running app silently.
if [ "$launch" = yes ] && [ "$(id -u)" -ne 0 ] && { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; }; then
    if [ "$was_running" = yes ]; then
        set -- --autostart
    else
        set --
    fi
    if command -v setsid >/dev/null 2>&1; then
        setsid "$launcher" "$@" >/dev/null 2>&1 </dev/null &
    else
        nohup "$launcher" "$@" >/dev/null 2>&1 </dev/null &
    fi
    say "Eye Care Reminder is running."
fi
