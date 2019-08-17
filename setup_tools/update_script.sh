#!/usr/bin/env bash
# Updates both the python package and the local git repo

# CD to the location of the package
# Could be ~/kavalkilu or ~/projects/kavalkilu
cd ${HOME}
if [[ -d "projects" ]]
then
    KAVDIR=${HOME}/projects/kavalkilu
else
    KAVDIR=${HOME}/kavalkilu
fi

cd ${KAVDIR}

echo "Pulling update from git repo"
git pull origin master

# Then update the python package locally
echo "Beginning update of python package"
sudo pip3 install -e git+https://github.com/barretobrock/kavalkilu.git#egg=kavalkilu --upgrade

echo "Process completed"