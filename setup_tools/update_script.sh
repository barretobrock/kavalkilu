#!/usr/bin/env bash
# Updates both the python package and the local git repo

# CD to the location of the package and pull from master
# Could be ~/kavalkilu or ~/projects/kavalkilu
KAVDIR=${HOME}/kavalkilu
LT_KAVDIR=${HOME}/projects/kavalkilu

if [[ -d ${LT_KAVDIR} ]]
then
    # Laptop
    KAVDIR=${LT_KAVDIR}
fi

echo "Pulling update from git repo"
# TODO see if I can check if master is up to date before issuing command. If it is, don't pull
(cd ${KAVDIR} && git pull origin master)

# Then update the python package locally
echo "Beginning update of python package"
#(cd ${KAVDIR} &&
# TODO check if installed, then upgrade if so
pip3 install git+https://github.com/barretobrock/kavalkilu.git#egg=kavalkilu --upgrade

# Apply cronjob changes, if any.
echo "Checking for crontab updates"
MACHINE_HOSTNAME=${HOSTNAME}
CRON_FILE=${KAVDIR}/documentation/crons/${MACHINE_HOSTNAME}.sh
if [[ -f ${CRON_FILE} ]]
then
    # Matching file found. Apply as update to cronjobs
    echo "Found matching cronjob file for ${CRON_FILE}. Applying changes..."
    crontab ${CRON_FILE}
else
    echo "No matching cronjob file found for ${CRON_FILE}."
fi

printf "===============\nProcess completed\n"