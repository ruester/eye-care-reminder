#!/bin/sh
# Self-extracting header for the Eye Care Reminder Linux installer.
# `just build-linux` appends a gzipped tarball of the payload (installer/, app/,
# VERSION) after the __PAYLOAD_BELOW__ marker; this header extracts it to a
# temporary directory and runs installer/install.sh with the given arguments.
set -eu

for tool in awk tail tar gzip mktemp; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "error: the installer needs '$tool', which is not installed." >&2
        exit 1
    fi
done

payload_line=$(awk '/^__PAYLOAD_BELOW__$/ { print NR + 1; exit 0 }' "$0")
workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT
trap 'exit 130' INT TERM

tail -n +"$payload_line" "$0" | tar -xz -C "$workdir"
sh "$workdir/installer/install.sh" "$@"
exit 0
# shellcheck disable=SC2317
__PAYLOAD_BELOW__
