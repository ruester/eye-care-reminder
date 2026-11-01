#!/bin/sh
# End-to-end test of the Linux installer (run by CI, like Test-Installer.ps1 on Windows):
# installs an old build for a throwaway user home, checks that the app runs and opens
# its settings (single instance), upgrades to the new build while the app is running
# (settings kept, app restarted), uninstalls while it is running (no leftovers) and,
# if passwordless sudo is available, installs and uninstalls for all users.
#
# Needs an X display and a session D-Bus, e.g.:
#   xvfb-run -a dbus-run-session sh src/linux/tests/test-installer.sh OLD.bin NEW.bin VERSION
# and xdotool to find the settings window.
set -eu

old_bin=$(realpath "$1")
new_bin=$(realpath "$2")
expected_version=$3

HOME=$(mktemp -d)
export HOME
unset XDG_DATA_HOME XDG_CONFIG_HOME
export LANG=C.UTF-8 XDG_CURRENT_DESKTOP=XFCE
app_dir=$HOME/.local/share/eye-care-reminder
launcher=$HOME/.local/bin/eye-care-reminder
settings=$HOME/.config/eye-care-reminder/settings.ini

failed=0
check() {
    description=$1
    shift
    if "$@"; then
        echo "ok:   $description"
    else
        echo "FAIL: $description"
        failed=1
    fi
}

instances() { pgrep -f "$app_dir/eye-care-reminder.py" | wc -l; }

# Polls up to 15 s until the command succeeds.
wait_for() {
    i=0
    while ! "$@"; do
        i=$((i + 1))
        [ "$i" -lt 30 ] || return 1
        sleep 0.5
    done
}

settings_window() { xdotool search --name "^Eye Care Reminder - Settings$" >/dev/null 2>&1; }
one_instance() { [ "$(instances)" -eq 1 ]; }
no_instance() { [ "$(instances)" -eq 0 ]; }
version_is() { [ "$("$launcher" --version)" = "Eye Care Reminder $1" ]; }

echo "== Install the old build (fresh install: the app starts and opens its settings)"
sh "$old_bin"
check "app directory" test -f "$app_dir/eye-care-reminder.py"
check "uninstaller" test -f "$app_dir/uninstall.sh"
check "launcher" test -x "$launcher"
check "menu entry" grep -q "^Exec=\"$launcher\"$" "$HOME/.local/share/applications/eye-care-reminder.desktop"
check "autostart entry" grep -q "^Exec=\"$launcher\" --autostart$" "$HOME/.config/autostart/eye-care-reminder.desktop"
check "icon" test -f "$HOME/.local/share/icons/hicolor/48x48/apps/eye-care-reminder.png"
check "old version" version_is 0.0.0
check "app is running" wait_for one_instance
check "settings window is open" wait_for settings_window
check "first run saved the settings" wait_for test -f "$settings"

echo "== Start the app again (single instance)"
xdotool search --name "^Eye Care Reminder - Settings$" windowclose 2>/dev/null || true
"$launcher"
check "settings window opens again" wait_for settings_window
check "still one instance" one_instance

echo "== Upgrade while the app is running"
printf '[settings]\ninterval_minutes = 25\nauto_hide = false\nauto_hide_seconds = 30\nlanguage = cs\n' > "$settings"
sh "$new_bin"
check "new version" version_is "$expected_version"
check "app is running again" wait_for one_instance
check "restarted with --autostart" wait_for pgrep -f "eye-care-reminder.py --autostart" >/dev/null
check "settings kept" grep -q "interval_minutes = 25" "$settings"
check "language kept" grep -q "language = cs" "$settings"

echo "== Uninstall while the app is running"
sh "$app_dir/uninstall.sh"
check "app stopped" wait_for no_instance
check "app directory removed" test ! -e "$app_dir"
check "launcher removed" test ! -e "$launcher"
check "menu entry removed" test ! -e "$HOME/.local/share/applications/eye-care-reminder.desktop"
check "autostart entry removed" test ! -e "$HOME/.config/autostart/eye-care-reminder.desktop"
check "icons removed" test -z "$(find "$HOME/.local/share/icons" -name 'eye-care-reminder*')"
check "settings kept after uninstall" test -f "$settings"

if sudo -n true 2>/dev/null; then
    echo "== Install for all users (root)"
    sudo -n sh "$new_bin" --no-launch
    check "app in /opt" test -f /opt/eye-care-reminder/eye-care-reminder.py
    check "launcher in /usr/local/bin" test -x /usr/local/bin/eye-care-reminder
    check "system autostart entry" test -f /etc/xdg/autostart/eye-care-reminder.desktop
    check "version" [ "$(/usr/local/bin/eye-care-reminder --version)" = "Eye Care Reminder $expected_version" ]
    sudo -n sh /opt/eye-care-reminder/uninstall.sh
    check "removed from /opt" test ! -e /opt/eye-care-reminder
    check "system autostart entry removed" test ! -e /etc/xdg/autostart/eye-care-reminder.desktop
fi

pkill -f "$app_dir/eye-care-reminder.py" 2>/dev/null || true
rm -rf "$HOME"
if [ "$failed" -ne 0 ]; then
    echo "Installer checks failed."
    exit 1
fi
echo "All installer checks passed."
