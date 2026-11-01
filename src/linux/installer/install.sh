#!/bin/sh
# Eye Care Reminder - Linux installer (run by the self-extracting .bin, see header.sh).
#
# Installs the app (Python 3 + GTK 3, the same for every desktop environment;
# Xfce is the primary target) with a menu entry and an autostart entry:
#   - as a normal user: for this user only (~/.local/share/eye-care-reminder),
#   - as root: for all users (/opt/eye-care-reminder).
# Running a newer .bin upgrades in place. The installed copy of this script,
# <app dir>/uninstall.sh, removes the app again (same as --uninstall).
set -eu

APP=eye-care-reminder
PAYLOAD_DIR=$(cd "$(dirname "$0")/.." && pwd)

usage() {
    cat <<USAGE
Usage: $APP-<version>-linux.bin [--no-launch] [--uninstall]

Installs Eye Care Reminder for the current user, or for all users when run as root.

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

# --- Requirements: Python 3 with GTK 3 (PyGObject) and cairo ---
find_python() {
    for candidate in /usr/bin/python3 "$(command -v python3 2>/dev/null || true)"; do
        if [ -n "$candidate" ] && [ -x "$candidate" ] && "$candidate" -c '
import gi
gi.require_version("Gtk", "3.0")
gi.require_foreign("cairo")
' >/dev/null 2>&1; then
            echo "$candidate"
            return
        fi
    done
}

install_command() {
    if command -v apt-get >/dev/null 2>&1; then
        echo "apt-get install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf install -y python3 python3-gobject python3-cairo gtk3"
    elif command -v zypper >/dev/null 2>&1; then
        echo "zypper --non-interactive install python3 python3-gobject python3-gobject-cairo python3-gobject-Gdk typelib-1_0-Gtk-3_0"
    elif command -v pacman >/dev/null 2>&1; then
        echo "pacman -S --needed --noconfirm python python-gobject python-cairo gtk3"
    fi
}

python=$(find_python)
if [ -z "$python" ]; then
    say "Eye Care Reminder needs Python 3 with GTK 3 (PyGObject), which is not installed."
    command=$(install_command)
    if [ -z "$command" ]; then
        fail "Install Python 3, PyGObject (GTK 3) and pycairo with your package manager, then run this installer again."
    fi
    if [ "$(id -u)" -eq 0 ]; then
        run_command=$command
    else
        run_command="sudo $command"
    fi
    answer=n
    if (: </dev/tty) 2>/dev/null; then
        printf 'Install it now with "%s"? [Y/n] ' "$run_command" >/dev/tty
        read -r answer </dev/tty || answer=n
        [ -n "$answer" ] || answer=y
    fi
    case "$answer" in
        y|Y|yes|Yes) sh -c "$run_command" || fail "Installing the requirements failed." ;;
        *) fail "Install the requirements with \"$run_command\", then run this installer again." ;;
    esac
    python=$(find_python)
    [ -n "$python" ] || fail "Python 3 with GTK 3 is still not available."
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

case "$(printf '%s' "${XDG_CURRENT_DESKTOP:-}" | tr '[:upper:]' '[:lower:]')" in
    *xfce*|"") ;;
    *) say "Note: Eye Care Reminder is made for Xfce. On other desktops the reminders work, but the tray icon needs a desktop with a notification area / AppIndicator support." ;;
esac

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
