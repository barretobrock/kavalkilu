#!/usr/bin/env bash

# SETUP
# --------------
# FILE PATHS
FUNCTIONS=./setup_tools/general_functions.sh

# Import common functions
. ${FUNCTIONS} --source-only

# Allow for faster response in SSH
# Add "IPQoS 0x00" to /etc/ssh/sshd_config
echo "IPQoS 0x00" | sudo tee -a /etc/ssh/sshd_config

# Create directories
mkdir data keys logs extras

sudo apt update && sudo apt upgrade
# Install python dependencies
sudo apt install git git-core python3-pip python3-dev python3-pandas python3-mysqldb python3-rpi.gpio \
    python3-serial wiringpi
# Install package dependencies
sudo pip3 install Adafruit_DHT sqlalchemy selenium phue amcrest slackclient==1.3.1 picamera pushbullet.py roku \
    paramiko beautifulsoup4 psutil tabulate

# Clone kavalkilu to home dir
git clone https://github.com/barretobrock/kavalkilu.git

# To run some of the scripts, bash is recommended over dash.
#   To reconfigure `sh` to point to bash, run this
sudo dpkg-reconfigure dash

# Locale fixing
echo -e "LANGUAGE=en_US.UTF-8\nLC_ALL=en_US.UTF-8\nLC_TIME=en_US.UTF-8\nLANG=en_US.UTF-8" | sudo tee /etc/default/locale
. /etc/default/locale

# Store git credentials to avoid prompt
echo "Beginning git credential storage"
git config --global credential.helper store
cd kavalkilu && git pull

# Set environment variables
#echo -e "\nexport KAVPY=/usr/bin/python3\nexport KAVDIR=${HOME}/kavalkilu" >> ~/.bashrc

echo "Setup complete."