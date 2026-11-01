#!/usr/bin/env bash
# Commits .github/badges/<platform>-coverage.svg to main, only when it changes
# (used by the Windows and Linux jobs of build.yml on pushes to main).
# Usage: publish-coverage-badge.sh <Platform> <percent>; needs GH_TOKEN.
# Pushes made with GITHUB_TOKEN don't trigger workflows.
set -euo pipefail

platform=$1
percent=$2
[[ "$percent" =~ ^[0-9]+$ ]] || { echo "Invalid coverage percentage: $percent" >&2; exit 1; }
name="$(tr '[:upper:]' '[:lower:]' <<<"$platform")-coverage.svg"
if ((percent >= 80)); then color=brightgreen
elif ((percent >= 60)); then color=green
elif ((percent >= 40)); then color=yellow
elif ((percent >= 20)); then color=orange
else color=red
fi

svg="$RUNNER_TEMP/$name"
curl -fsSL --retry 3 -o "$svg" \
    "https://img.shields.io/badge/${platform}%20unit%20test%20coverage-${percent}%25-${color}"

remote="https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
for attempt in 1 2 3; do
    # Fresh clone of the latest main, so the build checkout stays untouched.
    dir="$RUNNER_TEMP/badge-$platform-$attempt"
    git clone -q --depth 1 --branch main "$remote" "$dir"
    mkdir -p "$dir/.github/badges"
    cp "$svg" "$dir/.github/badges/$name"
    git -C "$dir" add ".github/badges/$name"
    if git -C "$dir" diff --cached --quiet; then
        echo "$platform coverage badge unchanged ($percent%)"
        exit 0
    fi
    git -C "$dir" -c user.name="github-actions[bot]" \
        -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
        commit -q -m "Update $platform coverage badge to $percent%"
    if git -C "$dir" push -q origin HEAD:main; then
        echo "$platform coverage badge updated to $percent%"
        exit 0
    fi
    echo "Push rejected (main moved), retrying"
done
echo "Could not push the $platform coverage badge to main" >&2
exit 1
