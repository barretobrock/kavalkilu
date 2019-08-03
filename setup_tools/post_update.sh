#!/usr/bin/env bash
# Posts an update to the package
#   1. Increments version, updates date
#   2. Commits changes & pushes

LEVEL=${1:-"patch"}  # Can be major, minor, patch

CURDIR="$(pwd)"
cd ${HOME}
if [[ -d "projects" ]]
then
    KAVDIR=${HOME}/projects/kavalkilu
else
    KAVDIR=${HOME}/kavalkilu
fi
cd ${KAVDIR}

# Kick off setup.py
python3 increment_version.py "--$LEVEL"

# Next, find the current branch name
BRANCH="$(git symbolic-ref HEAD 2>/dev/null)" || BRANCH="(unnamed branch)"     # detached HEAD
BRANCH=${BRANCH##refs/heads/}

# commit and ready for push
git add ${KAVDIR}/__init__.py
git commit -m "Auto increment version"
git push origin ${BRANCH}
