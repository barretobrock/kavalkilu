#!/usr/bin/env bash

# SETUP
# --------------
# FILE PATHS
FUNCTIONS=./setup_tools/general_functions.sh

# Import common functions
. ${FUNCTIONS} --source-only

KAVDIR=${HOME}/projects/kavalkilu
MACHINE_HOSTNAME=${HOSTNAME}
CRON_DIR=${KAVDIR}/documentation/crons
CRON_FILE=${CRON_DIR}/${MACHINE_HOSTNAME}.sh
SUDO_CRON_FILE=${CRON_DIR}/su-${MACHINE_HOSTNAME}.sh

echo "${CRON_FILE}"

announce_section "Here's a section coming up!"