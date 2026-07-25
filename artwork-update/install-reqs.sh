#!/usr/bin/bash
#
# install-reqs.sh
#
# Description:
#   Installs every dependency the scripts in this directory need, as
#   documented in each script's own doc under DOCS/. This is the union of
#   every "Installation" section in DOCS/README-*.md:
#     - Python packages (via pip): mutagen, musicbrainzngs, requests,
#       Pillow, itunespy
#     - System packages (via apt): mp3gain, mp3val
#   Not every script needs every package — see the individual doc in DOCS/
#   for exactly which packages a given script requires.
#
# Requirements:
#   - python3 with pip
#   - apt (Debian/Ubuntu); on other systems, install mp3gain and mp3val
#     manually and re-run this script to handle the pip packages only
#
# Usage:
#   ./install-reqs.sh
#

set -e

# ----------------------------------------------------------------------------
# Python packages
# ----------------------------------------------------------------------------

# One combined install call is faster than one pip invocation per package
# and lets pip resolve everything's dependencies together.
PYTHON_PACKAGES=(mutagen musicbrainzngs requests Pillow itunespy)

echo "🐍 Installing Python packages: ${PYTHON_PACKAGES[*]}"

pip_error_log=$(mktemp)
trap 'rm -f "$pip_error_log"' EXIT

if ! python3 -m pip install "${PYTHON_PACKAGES[@]}" 2>"$pip_error_log"; then
    if [[ -z "$VIRTUAL_ENV" ]] && grep -q "externally-managed-environment" "$pip_error_log"; then
        # Debian 12+/Ubuntu 23.04+ block pip from touching the system Python
        # (PEP 668) unless a venv is active. $VIRTUAL_ENV is empty, confirming
        # no venv is active here, so fall back to --break-system-packages,
        # same as this container's own setup requires. This does carry real
        # risk of clashing with apt-managed Python packages; a venv is the
        # safer long-term fix.
        echo "⚠️  pip refused (externally-managed-environment / PEP 668), no venv active."
        echo "   Retrying with --break-system-packages..."
        python3 -m pip install --break-system-packages "${PYTHON_PACKAGES[@]}"
    else
        # Either a real install error, or externally-managed-environment
        # while a venv IS active (unexpected — venvs should never hit that
        # check). Don't paper over either case with --break-system-packages.
        cat "$pip_error_log" >&2
        exit 1
    fi
fi

# ----------------------------------------------------------------------------
# System packages (apt)
# ----------------------------------------------------------------------------

# Only prompt for packages that aren't already on $PATH, so re-running this
# script after a partial install doesn't re-prompt for everything.
apt_packages_needed=()
command -v mp3gain >/dev/null 2>&1 || apt_packages_needed+=("mp3gain")
command -v mp3val >/dev/null 2>&1 || apt_packages_needed+=("mp3val")

if [[ ${#apt_packages_needed[@]} -eq 0 ]]; then
    echo "✅ mp3gain and mp3val already installed."
else
    if ! command -v apt >/dev/null 2>&1; then
        echo "⚠️  'apt' not found. Install manually on non-Debian systems: ${apt_packages_needed[*]}" >&2
        exit 1
    fi

    echo "📦 The following system packages are required but not installed:"
    printf '   - %s\n' "${apt_packages_needed[@]}"
    read -rp "Install them now via apt? [Y/n] " reply
    reply="${reply,,}"  # to lowercase
    if [[ "$reply" =~ ^(y|yes|)$ ]]; then
        sudo apt update && sudo apt install -y "${apt_packages_needed[@]}"
    else
        echo "Skipped. Install manually before running scripts that need them: ${apt_packages_needed[*]}"
    fi
fi

echo "✅ Done."
