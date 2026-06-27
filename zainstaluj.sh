#!/usr/bin/env bash
# Launcher instalatora moda dla Linuxa.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo
    echo "  Nie znalazlem Pythona 3."
    echo "  Zainstaluj go menedzerem pakietow swojej dystrybucji, np.:"
    echo "    Debian/Ubuntu:  sudo apt install python3"
    echo "    Fedora:         sudo dnf install python3"
    echo "    Arch:           sudo pacman -S python"
    echo
    exit 1
fi

exec "$PY" "$DIR/installer.py" "$@"
