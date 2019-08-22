#!/usr/bin/env bash
# Posts an update to the package
#   1. Increments version, updates date
#   2. Commits changes & pushes

LEVEL=${1:-"patch"}  # Can be major, minor, patch

KAVDIR=${HOME}/projects/kavalkilu

# Kick off setup.py
VERSION=$(python3 ${KAVDIR}/increment_version.py "--${LEVEL}")

# commit and ready for push
git add ${KAVDIR}/__init__.py
git tag -a v${VERSION} -m "Auto increment to v${VERSION}"
git push origin : v${VERSION}
