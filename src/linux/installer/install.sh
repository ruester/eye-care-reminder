#!/bin/sh
# Eye Care Reminder - Linux installer.
# Detects the desktop environment (Xfce, Unity) and installs the matching
# variant. Falls back to the generic freedesktop.org notification variant.
set -eu

PAYLOAD_DIR=$(cd "$(dirname "$0")/.." && pwd)
SUPPORTED="xfce unity freedesktop"

usage() {
    cat <<USAGE
Usage: eye-care-reminder-linux.bin [--de=xfce|unity|freedesktop] [--prefix=DIR]

  --de=NAME      Skip detection and install the variant for NAME.
  --prefix=DIR   Installation directory (default: /opt/eye-care-reminder as
                 root, ~/.local/share/eye-care-reminder otherwise).
  -h, --help     Show this help.
USAGE
}

is_xfce_installed() {
    command -v xfce4-session >/dev/null 2>&1 || [ -f /usr/share/xsessions/xfce.desktop ]
}

is_unity_installed() {
    command -v unity >/dev/null 2>&1 || [ -f /usr/share/xsessions/unity.desktop ]
}

# Desktop of the current session, if it is one we know.
current_session_de() {
    case "$(printf '%s' "${XDG_CURRENT_DESKTOP:-}" | tr '[:upper:]' '[:lower:]')" in
        *xfce*) echo xfce ;;
        *unity*) echo unity ;;
        *) echo "" ;;
    esac
}

ask_de() {
    suggestion=$1
    if ! (: </dev/tty) 2>/dev/null; then
        echo "error: cannot determine the desktop environment unambiguously and no terminal is available." >&2
        echo "       Re-run with --de=xfce, --de=unity or --de=freedesktop." >&2
        exit 1
    fi
    {
        echo "Which desktop environment do you use?"
        echo "  1) Xfce"
        echo "  2) Unity (Ubuntu)"
        echo "  3) Other (generic freedesktop.org notifications)"
    } >/dev/tty
    while :; do
        if [ -n "$suggestion" ]; then
            printf 'Selection [%s]: ' "$suggestion" >/dev/tty
        else
            printf 'Selection: ' >/dev/tty
        fi
        read -r answer </dev/tty || exit 1
        [ -z "$answer" ] && answer=$suggestion
        case "$answer" in
            1|xfce) echo xfce; return ;;
            2|unity) echo unity; return ;;
            3|freedesktop|other) echo freedesktop; return ;;
            *) echo "Please enter 1, 2 or 3." >/dev/tty ;;
        esac
    done
}

detect_de() {
    xfce=no; unity=no
    is_xfce_installed && xfce=yes
    is_unity_installed && unity=yes

    if [ "$xfce" = yes ] && [ "$unity" = no ]; then
        echo xfce
    elif [ "$unity" = yes ] && [ "$xfce" = no ]; then
        echo unity
    else
        # Both or neither installed: let the user decide.
        ask_de "$(current_session_de)"
    fi
}

de=""
if [ "$(id -u)" -eq 0 ]; then
    prefix=/opt/eye-care-reminder
else
    prefix="${XDG_DATA_HOME:-$HOME/.local/share}/eye-care-reminder"
fi

for arg in "$@"; do
    case "$arg" in
        --de=*) de=${arg#--de=} ;;
        --prefix=*) prefix=${arg#--prefix=} ;;
        -h|--help) usage; exit 0 ;;
        *) echo "error: unknown argument: $arg" >&2; usage >&2; exit 1 ;;
    esac
done

if [ -z "$de" ]; then
    de=$(detect_de)
fi

case " $SUPPORTED " in
    *" $de "*) ;;
    *) echo "error: unsupported desktop environment: $de (supported: $SUPPORTED)" >&2; exit 1 ;;
esac

echo "Installing Eye Care Reminder ($de variant) to $prefix ..."
mkdir -p "$prefix"
cp -R "$PAYLOAD_DIR/$de/." "$prefix/"
rm -f "$prefix/.keep"
echo "$de" > "$prefix/desktop-environment"
echo "Done."
