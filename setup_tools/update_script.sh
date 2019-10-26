#!/usr/bin/env bash
# Updates both the python package and the local git repo

# SETUP
# --------------
# FILE PATHS
FUNCTIONS=./setup_tools/general_functions.sh

# Import common functions
. ${FUNCTIONS} --source-only

# DIRECTORY SETUP
# CD to the location of the package and pull from master
# Could be ~/kavalkilu or ~/projects/kavalkilu
KAVDIR=${HOME}/kavalkilu
LT_KAVDIR=${HOME}/projects/kavalkilu

if [[ -d ${LT_KAVDIR} ]]; then
    # Laptop
    KAVDIR=${LT_KAVDIR}
fi

# GIT PULL
# --------------
announce_section "Pulling update from git repo"
# TODO see if I can check if master is up to date before issuing command. If it is, don't pull
(cd ${KAVDIR} && git pull origin master)

# PY PACKAGE UPDATE
# --------------
# Then update the python package locally
announce_section "Beginning update of python package"
# TODO check if installed, then upgrade if so
python3 -m pip install git+https://github.com/barretobrock/kavalkilu.git#egg=kavalkilu --upgrade

# CRON UPDATE
# --------------
# Apply cronjob changes, if any.
announce_section "Checking for crontab updates"
MACHINE_HOSTNAME=${HOSTNAME}
CRON_DIR=${KAVDIR}/documentation/crons
CRON_FILE=${CRON_DIR}/${MACHINE_HOSTNAME}.sh
SUDO_CRON_FILE=${CRON_DIR}/su-${MACHINE_HOSTNAME}.sh

[[ -f ${CRON_FILE} ]] && echo "Applying cron file." && crontab ${CRON_FILE} || echo "No cron file."
[[ -f ${SUDO_CRON_FILE} ]] && echo "Applying sudo cron file." && sudo crontab ${SUDO_CRON_FILE} || echo "No sudo cron file."

announce_section "Process completed"
