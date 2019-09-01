#!/usr/bin/env bash

# Allow for faster response in SSH
# Add "IPQoS 0x00" to /etc/ssh/sshd_config
echo "IPQoS 0x00" >> /etc/ssh/sshd_config

# Create directories
mkdir data keys logs extras

# Install python dependencies
sudo apt-get install git git-core python3-pip python3-dev python3-pandas python3-mysqldb python3-rpi.gpio \
    python3-serial wiringpi
# Install package dependencies
sudo pip3 install Adafruit_DHT sqlalchemy selenium phue amcrest slackclient==1.3.1 picamera pushbullet.py roku \
    paramiko beautifulsoup4 psutil

# Clone kavalkilu to home dir
git clone https://github.com/barretobrock/kavalkilu.git

# Store git credentials to avoid prompt
echo "Beginning git credential storage"
git config --global credential.helper store
git pull
