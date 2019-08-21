# kavalkilu
Some updated scripts for personal use throughout various personal projects (mostly Raspberry Pi-centric)

## Installation
```bash
sudo pip3 install git+https://github.com/barretobrock/kavalkilu.git  
```

## Update
```bash
sudo pip3 install git+https://github.com/barretobrock/kavalkilu.git --upgrade
```

## Testing
 - First, tag the commit
    ```bash
    git tag -a qa -m "KILU-1: QA Testing"
    ```
 - Then, install
    ```bash
    sudo pip3 install -e git+https://github.com/barretobrock/kavalkilu.git@qa#egg=kavalkilu_qa
    ```

## Troubleshooting
 - **EDIT: This no longer seems necessary** 
    First time building a proper package, so there's a lot that might go wrong. 
    - Currently, there's an issue with the package not updating when using `pip`.
        To bypass this, I copy the contents of the package directory to the 
        package location in `site-packages`:
        `sudo cp -r ~/kavalkilu ~/.local/lib/python3.6/site-packages`
 - Debugging from crontab
   `nano /var/log/syslog`

## Tips


## Raspberry Pi-Specific

### SD Card prep
 - Find Card 
    `lsblk`
 - Unmount the card
    `umount /dev/mmcblk0`
 - Wipe SD card
    `sudo dd if=/dev/zero of=/dev/mmcblk0 bs=8192 status=progress`
 - Load Raspberry Pi image
    `sudo dd if=~/Documents/distros/2019-07-10-raspbian-buster-lite.img of=/dev/mmcblk0 conv=fsync status=progress bs=4M`

#### Configurations from SD card
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
 - add `/boot/ssh`
     - empty file
     
#### Saving configs
 - Save a compressed img from the SD card for easier distribution among all RasPis
    `sudo dd if=/dev/mmcblk0 bs=32M status=progress | gzip -c > ~/Documents/distros/2019-08-18-raspi-with-config.img.gz`
 - When duplicating to another card, use this:
    `gzip -cd < ~/Documents/distros/2019-08-18-raspi-with-config.img.gz | sudo dd of=/dev/mmcblk0 bs=32M status=progress`
 


### Initial run
 - Make configurations (change pw, hostname, locale, enable SSH, etc)
    `sudo raspi-config`
    - change pw
    - set hostname
    - set network
    - enable ssh
 - Edit .bashrc to enforce locale changes
    ```bash
    sudo nano .bashrc
    export LC_ALL=en_US.UTF-8
    export LANG=en_US.UTF-8
    export LANGUAGE=en_US.UTF-8
    ```

### Environment Setup Option 1: Docker

#### Docker Install
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

### Environment Setup Option 2: The Old & Busted Option
    __Note: 
        This is to prepare a Raspberry Pi device for installation of this package. 
        This is mildly different from a requirements.txt file.__ 

 - Install git and others
    ```bash
    # Install support components
    sudo apt-get install git git-core python3-pip python3-dev python3-pandas python3-mysqldb python3-rpi.gpio
    # Install packages
    sudo pip3 install Adafruit_DHT sqlalchemy selenium
    # Make directories for storing things
    mkdir data keys logs extras
    # Add in kavalkilu repo
    git clone https://github.com/barretobrock/kavalkilu.git
    ```
 - Install wiringPi
    ```bash
    cd extras
    # Clone in WiringPi
    git clone git://git.drogon.net/wiringPi
    cd wiringPi
    # Build the file
    ./build
    ```
    
### Optional Installs


