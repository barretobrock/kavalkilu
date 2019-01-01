#!/usr/bin/env bash
# Updates both the python package and the local git repo

echo "Beginning update of python package"
# Update the python package
sudo pip3 install git+https://github.com/barretobrock/kavalkilu.git --upgrade

echo "Beginning update of git repo"
# Update the repo
cd ~/kavalkilu/
git pull origin master
cd ~

echo "Process completed"