#!/usr/bin/env bash
# Updates both the python package and the local git repo

# CD to the location of the package and pull from master
# Could be ~/kavalkilu or ~/projects/kavalkilu
KAVDIR=${HOME}/kavalkilu
if [[ ! -d "projects" ]]
then
    # Laptop
    KAVDIR=${HOME}/projects/kavalkilu
fi

echo "Pulling update from git repo"
(cd ${KAVDIR} && git pull origin master)

# Then update the python package locally
echo "Beginning update of python package"
#(cd ${KAVDIR} &&
# TODO check if installed, then upgrade if so
sudo pip3 install --editable git+https://github.com/barretobrock/kavalkilu.git#egg=kavalkilu --upgrade

echo "Process completed"