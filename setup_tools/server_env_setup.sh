#!/usr/bin/env bash

# Create directories
mkdir data keys logs extras

# Install python dependencies
sudo apt-get install git git-core python3-pip python3-dev python3-pandas python3-mysqldb \
    python3-serial
# Install package dependencies
sudo pip3 install sqlalchemy selenium phue amcrest slackclient==1.3.1 pushbullet.py roku \
    paramiko beautifulsoup4 psutil tabulate daemonize markovify

# Clone kavalkilu to home dir
git clone https://github.com/barretobrock/kavalkilu.git ${HOME}

# To run some of the scripts, bash is recommended over dash.
#   To reconfigure `sh` to point to bash, run this
# TODO Check if dash is default first
sudo dpkg-reconfigure dash

# Store git credentials to avoid prompt
echo "Beginning git credential storage"
git config --global credential.helper store
git pull

# Set environment variables
#echo -e "\nexport KAVPY=/usr/bin/python3\nexport KAVDIR=${HOME}/kavalkilu" >> ~/.bashrc