# kavalkilu
Some updated scripts for personal use throughout various personal projects (mostly Raspberry Pi-centric).
The main focus of these scripts is in home automation, but more precisely it's a little bit of everything.

## Installation
```bash
pip3 install git+https://github.com/barretobrock/kavalkilu.git  
```

## Update
```bash
pip3 install git+https://github.com/barretobrock/kavalkilu.git --upgrade
```

## Testing
 1. Commits on the `develop` branch
 2. `checkout` the develop branch, perform tests.
 3. `merge` `develop` with `master` (asuming all went well.)

## Setup
### Raspberry Pi
#### Raspi SD Card prep
 - Find Card 
    `lsblk`
 - Unmount the card
    `umount /dev/mmcblk0`
 - Wipe SD card
    `sudo dd if=/dev/zero of=/dev/mmcblk0 bs=8192 status=progress`
 - Load Raspberry Pi image
    `sudo dd if=~/Documents/distros/2019-07-10-raspbian-buster-lite.img of=/dev/mmcblk0 conv=fsync status=progress bs=4M`
#### Initial run
 - Make configurations (change pw, hostname, locale, enable SSH, etc)
    `sudo raspi-config`
    - change pw, set network, locale, enable ssh
 - Edit .bashrc to enforce locale changes
    `echo -e "\nLC_ALL=en_US.UTF-8\nLANG=en_US.UTF-8\nLANGUAGE=en_US.UTF-8" | tee -a sudo nano .bashrc`
### Environment Setup with Script
_Note: This is to prepare a Raspberry Pi device for installation of this package. This is now to supplement the requirements put in the `setup.py` file._ 

 - Install git and others
    ```bash
    # Install support components
    sudo apt-get install git git-core python3-pip python3-dev python3-pandas python3-mysqldb python3-rpi.gpio
    # Make directories for storing things
    mkdir data keys logs extras
    # Add in kavalkilu repo
    git clone https://github.com/barretobrock/kavalkilu.git
    ```


## Troubleshooting
### git
 - After git account setup, still prompting for passphrase
    `ssh-add ~/.ssh/id_rsa`
    - Long term fix: Add the following to `~/.bashrc`
    ```bash
    if [ ! -S ~/.ssh/ssh_auth_sock ]; then
      eval `ssh-agent`
      ln -sf "$SSH_AUTH_SOCK" ~/.ssh/ssh_auth_sock
    fi
    export SSH_AUTH_SOCK=~/.ssh/ssh_auth_sock
    ssh-add -l > /dev/null || ssh-add
    ```
### python
 - TBD
### crontab
 - Debugging from crontab
    `tail -f /var/log/syslog`
### raspi
 - ssh slow to respond
    `echo "IPQoS 0x00" | sudo tee -a /etc/ssh/sshd_config`

## Tips
 - TBA!

## Future Development & Testing
### Porting SSH & Wifi Configurations straight from SD card after writing
_Note: This was tested and failed to produce results. Will be revisited at some point._
 - card in `/media/${USER}`
 - add `/boot/wpa_supplicant.conf`:
    - setup:
    ```
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=US
    
    network={
        ssid=""
        psk=""
        key_mgmt=WPA-PSK
    }
    ```
 - add "IPQoS 0x00" to /etc/ssh/sshd_config (if possible)
 - add `/boot/ssh`
     - empty file    
### Saving configs from one card & duplicating to others
_Note: This might be abandoned, as writing to the card writes the entire card, regardless of empty space._
 - Save a compressed img from the SD card for easier distribution among all RasPis
    `sudo dd if=/dev/mmcblk0 bs=32M status=progress | gzip -c > ~/Documents/distros/2019-08-18-raspi-with-config.img.gz`
 - When duplicating to another card, use this:
    `gzip -cd < ~/Documents/distros/2019-08-18-raspi-with-config.img.gz | sudo dd of=/dev/mmcblk0 bs=32M status=progress`
 
### Environment Setup With Docker
#### Docker Install
_Note: This was a good idea, but a road block in this is that it was difficult to get RasPi components to communicate "out of the box" with the docker instance_
 - install some dependencies
    ```bash
    sudo apt get update
    sudo apt install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common
    ```
 - get Docker signing key for packages
    `curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | sudo apt-key add -`
 - add official Docker repo
    ```bash
    echo "deb [arch=armhf] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
     $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list
    ```
 - install docker
    ```bash
    sudo apt update
    sudo apt install -y --no-install-recommends docker-ce cgroupfs-mount
    ```
 - enable docker on boot
    ```bash
    sudo systemctl enable docker
    sudo systemctl start docker
    ```
 - pull and run docker test image
    ```bash
    sudo docker run --rm arm32v7/hello-world
    ```
 - log in to account
    ```bash
    # Add current user to docker perms group to be able to login successfully
    sudo usermod -a -G docker ${USER}
    # Now we can login
    docker login
    ```



