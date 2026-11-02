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

echo "== Compatibility check"
fakes=$(mktemp -d)
printf '#!/bin/sh\necho 3.6\n' > "$fakes/old-python"
printf '#!/bin/sh\necho 3.12 gi\n' > "$fakes/python-without-gtk"
printf '#!/bin/sh\necho 3.12 gi gtk cairo\n' > "$fakes/python-without-indicator"
printf '#!/bin/sh\necho 3.12 gi gtk cairo indicator\n' > "$fakes/python-with-indicator"
chmod +x "$fakes"/*
check "--check passes" sh "$new_bin" --check
check "--check reports compatible" sh -c "sh '$new_bin' --check | grep -q 'This system is compatible'"
check "old Python is rejected" sh -c "! EYE_CARE_REMINDER_PYTHON='$fakes/old-python' sh '$new_bin' --check </dev/null"
check "missing GTK is reported" sh -c "EYE_CARE_REMINDER_PYTHON='$fakes/python-without-gtk' sh '$new_bin' --check </dev/null | grep -q 'missing  GTK 3'"
check "missing Python is reported" sh -c "EYE_CARE_REMINDER_PYTHON=/nonexistent sh '$new_bin' --check </dev/null | grep -q 'missing  Python 3'"
check "no install with missing dependencies" sh -c "! EYE_CARE_REMINDER_PYTHON='$fakes/python-without-gtk' sh '$new_bin' </dev/null"
check "Unity is supported" sh -c "XDG_CURRENT_DESKTOP=Unity:Unity7:ubuntu EYE_CARE_REMINDER_PYTHON='$fakes/python-with-indicator' sh '$new_bin' --check </dev/null | grep -q 'ok       Desktop: Unity'"
check "Unity requires AppIndicator" sh -c "! XDG_CURRENT_DESKTOP=Unity:Unity7:ubuntu EYE_CARE_REMINDER_PYTHON='$fakes/python-without-indicator' sh '$new_bin' --check </dev/null"
check "missing AppIndicator is reported on Unity" sh -c "XDG_CURRENT_DESKTOP=Unity:Unity7:ubuntu EYE_CARE_REMINDER_PYTHON='$fakes/python-without-indicator' sh '$new_bin' --check </dev/null | grep -q 'missing  AppIndicator'"
check "AppIndicator is optional on Xfce" sh -c "EYE_CARE_REMINDER_PYTHON='$fakes/python-without-indicator' sh '$new_bin' --check </dev/null"
with_indicator="EYE_CARE_REMINDER_PYTHON='$fakes/python-with-indicator'"
without_indicator="EYE_CARE_REMINDER_PYTHON='$fakes/python-without-indicator'"
check "KDE requires AppIndicator" sh -c "! XDG_CURRENT_DESKTOP=KDE $without_indicator sh '$new_bin' --check </dev/null"
check "KDE is supported" sh -c "XDG_CURRENT_DESKTOP=KDE $with_indicator sh '$new_bin' --check </dev/null | grep -q 'ok       Desktop: KDE Plasma'"
check "GNOME requires the AppIndicator extension" sh -c "XDG_CURRENT_DESKTOP=ubuntu:GNOME $with_indicator sh '$new_bin' --check </dev/null | grep -q 'missing  GNOME Shell extension'"
extension_dir=$HOME/.local/share/gnome-shell/extensions/appindicatorsupport@rgcjonas.gmail.com
mkdir -p "$extension_dir"
check "GNOME with the extension is supported" sh -c "XDG_CURRENT_DESKTOP=ubuntu:GNOME $with_indicator sh '$new_bin' --check </dev/null | grep -q 'ok       GNOME Shell extension'"
rm -rf "$HOME/.local/share/gnome-shell"
check "Budgie is not GNOME" sh -c "XDG_CURRENT_DESKTOP=Budgie:GNOME $with_indicator sh '$new_bin' --check </dev/null | grep -q 'not officially supported'"
check "i3 without XDG_CURRENT_DESKTOP" sh -c "env -u XDG_CURRENT_DESKTOP I3SOCK=/tmp/i3-ipc $with_indicator sh '$new_bin' --check </dev/null | grep -q 'ok       Desktop: i3'"
check "nothing installed" test ! -e "$app_dir"
rm -rf "$fakes"

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
# The second start hands over to the running instance and exits; it must not hang.
check "second start returns" timeout 60 "$launcher"
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

echo "== i3: autostart line in the i3 config (i3 without dex)"
i3_config=$HOME/.config/i3/config
mkdir -p "$(dirname "$i3_config")"
printf 'bar {\n    status_command i3status\n}\n' > "$i3_config"
cp "$i3_config" "$i3_config.orig"
XDG_CURRENT_DESKTOP=i3 sh "$new_bin" --no-launch </dev/null
check "autostart line added" grep -qx "exec --no-startup-id \"$launcher\" --autostart" "$i3_config"
XDG_CURRENT_DESKTOP=i3 sh "$new_bin" --no-launch </dev/null
check "added only once" [ "$(grep -c -- "--autostart" "$i3_config")" -eq 1 ]
sh "$app_dir/uninstall.sh"
check "i3 config restored" cmp -s "$i3_config" "$i3_config.orig"
printf 'exec --no-startup-id dex --autostart --environment i3\n' > "$i3_config"
XDG_CURRENT_DESKTOP=i3 sh "$new_bin" --no-launch </dev/null
check "no line with dex" [ "$(grep -c "$launcher" "$i3_config")" -eq 0 ]
sh "$app_dir/uninstall.sh"
rm -rf "$HOME/.config/i3"

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
