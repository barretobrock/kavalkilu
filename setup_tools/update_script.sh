#!/usr/bin/env bash
# Updates both the python package and the local git repo

# Update the python package
sudo pip3 install git+https://github.com/barretobrock/kavalkilu.git --upgrade

# Update the repo
cd ~/kavalkilu/
git pull origin master
cd ~