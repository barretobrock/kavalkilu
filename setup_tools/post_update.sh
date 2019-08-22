#!/usr/bin/env bash
# Posts an update to the package
#   1. Increments version, updates date
#   2. Commits changes & pushes

LEVEL=${1:-"patch"}  # Can be major, minor, patch

KAVDIR=${HOME}/projects/kavalkilu
INC_VERS_FPATH=${KAVDIR}/increment_version.py

# Kick off setup.py
VERSION=$(python3 ${INC_VERS_FPATH} "--${LEVEL}")

# commit and ready for push
git add "${KAVDIR}/kavalkilu/__init__.py"
git tag -a "v${VERSION}" -m "Auto increment to v${VERSION}"
git push origin : v${VERSION}
