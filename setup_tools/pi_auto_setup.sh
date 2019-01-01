#!/bin/bash

# Raspberry pi setup script
### Very much WIP right now

# TODO: Add locale setup below:
1. insert the following into /etc/default/locale
    LANG=en_US.UTF-8
    LC_ALL=en_US.UTF-8
    LANGUAGE=en_US.UTF-8
2. Find way to uncomment the en_US section of /etc/locale.gen
3. Run `sudo locale-gen en_US.UTF-8`
4. Run `sudo update-locale en_US.UTF-8`

"""
 TODO!!!
    -change user password
    -change hostname
    -boot only to console (autologin)


    ### install git, wget
    sudo apt-get install wget git-core -y

    ### install Wiring pi
    git clone git://git.drogon.net/wiringPi
    cd ~/wiringPi
    git pull origin
    ./build

    ### install python3
    sudo apt-get install python3 python3-dev python3-pip

    ### install RPi.GPIO for python3
    sudo pip3 install RPi.GPIO

    ### install python GPIO
    sudo apt-get install python-dev python-rpi.gpio

    ### install pushbullet
    sudo pip3 install pushbullet.py

    ### install pi camera for python
    sudo apt-get install python3-picamera

    ### configure git for LPBOT
    git config --global user.name "barretobrock"
    git config --global user.email "barret.obrock@gmail.com"
    ### add directory for git
    mkdir /home/pi/LPBOT
    cd /home/pi/LPBOT
    ### initalize git
    git init
    ### pull files from GitHub
    git remote add origin https://github.com/barretobrock/LPBOT.git
    git pull origin master

    ### Dallas temp probe support material
    sudo modprobe w1-gpio && sudo modprobe w1_therm
    # Enable onw-wire
    sudo raspi-config
    # Open boot file
    sudo nano /boot/config.txt
    dtoverlay=w1-gpio-pullup,gpiopin=x,gpiopin=y # x,y = BCM pin1,pin2,pinx

    ### copy keys directory from hub pi to new
    scp -r pi@10.0.1.88:~/keys ~/keys

    ### install domoticz as slave
    sudo curl -L install.domoticz.com | sudo bash
    # on main domoticz server, go to Settings > Hardware, add remote domoticz server
"""


CONNECT_METHOD='wlan0'

if [[ $CONNECT_METHOD == *"wlan"* ]]; then
    # Get credentials from file
    WIFI_CRED_FILE="~/keys/wifi_creds.txt"
    WIFI_CREDS="`cat $WIFI_CRED_FILE`"
    echo "$WIFI_CREDS"

    # Extract wifi credentials into array
    arrWIFI_CREDS=(${WIFI_CREDS//;/ })
    WIFI_NAME=${arrWIFI_CREDS[0]}
    WIFI_PASS=${arrWIFI_CREDS[1]}
fi

# TODO refresh to connect without logging out

# Set

ADDRESS=(ip -f inet -o addr show $CONNECT_METHOD|cut -d\  -f 7 | cut -d/ -f 1)
NETMASK=ifconfig "$CONNECT_METHOD" | sed -rn '2s/ .*:(.*)$/\1/p'
NETWORK=
BROADCAST=(ifconfig | awk '/Bcast/ { print $3 }' | sed -e "s/^Bcast://")
GATEWAY=(/sbin/ip route | awk '/default/ { print $3 }')

INTERFACE_TEXT="auto lo\niface lo inet loopback\n\niface eth0 inet static\n\n"
