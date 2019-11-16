#!/usr/bin/env bash
# Updates both the python package and the local git repo

# ARGS
INSTALL_SPEED=${1:-full}    # Full, won't skip dependencies on pip install, fast will

NODEPS_FLAG=''
if [[ "${INSTALL_SPEED}" == "fast" ]];
then
    echo "Not pip installing dependencies"
    NODEPS_FLAG="--no-deps"
fi

# DIRECTORY SETUP
# CD to the location of the package and pull from master
REPO=kavalkilu
PROJDIR=${HOME}/kavalkilu

# SETUP
# --------------
# FILE PATHS
FUNCTIONS=${PROJDIR}/setup_tools/general_functions.sh

# Import common functions
. ${FUNCTIONS} --source-only

# GIT PULL
# --------------
announce_section "Pulling update from git repo"
(cd ${PROJDIR} && git pull origin master)

# PY PACKAGE UPDATE
# --------------
# Then update the python package locally
announce_section "Beginning update of python package"
python3 -m pip install git+https://github.com/barretobrock/${REPO}.git#egg=${REPO} --upgrade ${NODEPS_FLAG}

# CRON UPDATE
# --------------
# Apply cronjob changes, if any.
announce_section "Checking for crontab updates"
MACHINE_HOSTNAME=${HOSTNAME}
CRON_DIR=${PROJDIR}/documentation/crons
CRON_FILE=${CRON_DIR}/${MACHINE_HOSTNAME}.sh
SUDO_CRON_FILE=${CRON_DIR}/su-${MACHINE_HOSTNAME}.sh

[[ -f ${CRON_FILE} ]] && echo "Applying cron file." && crontab ${CRON_FILE} || echo "No cron file."
[[ -f ${SUDO_CRON_FILE} ]] && echo "Applying sudo cron file." && sudo crontab ${SUDO_CRON_FILE} || echo "No sudo cron file."

announce_section "Process completed"
