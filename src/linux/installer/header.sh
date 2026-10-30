#!/bin/sh
# Self-extracting header for the Eye Care Reminder Linux installer.
# `just build-linux` appends a gzipped tarball of the payload after the
# __PAYLOAD_BELOW__ marker; this header extracts it and runs install.sh.
set -eu

payload_line=$(awk '/^__PAYLOAD_BELOW__$/ { print NR + 1; exit 0 }' "$0")
workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT INT TERM

tail -n +"$payload_line" "$0" | tar -xz -C "$workdir"
sh "$workdir/installer/install.sh" "$@"
exit 0
# shellcheck disable=SC2317
__PAYLOAD_BELOW__
