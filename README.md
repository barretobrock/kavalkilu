# kavalkilu
Some updated scripts for personal use throughout various personal projects (mostly Raspberry Pi-centric)

## Installation
```bash
pip3 install git+https://github.com/barretobrock/kavalkilu.git  
```

## Update
```bash
pip3 install git+https://github.com/barretobrock/kavalkilu.git --upgrade
```

## Troubleshooting
 - **EDIT: This no longer seems necessary** 
    First time building a proper package, so there's a lot that might go wrong. 
    - Currently, there's an issue with the package not updating when using `pip`.
        To bypass this, I copy the contents of the package directory to the 
        package location in `site-packages`:
        `sudo cp -r ~/kavalkilu ~/.local/lib/python3.6/site-packages`

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
    `sudo dd if=~/Documents/distros/2018-11-13-raspbian-stretch-lite.img of=/dev/mmcblk0 conv=fsync status=progress bs=4M`

### Initial run
 - Make configurations (change pw, hostname, locale, enable SSH, etc)
    `sudo raspi-config`
 - Edit .bashrc to enforce locale changes
    ```bash
    sudo nano .bashrc
    export LC_ALL=en_US.UTF-8
    export LANG=en_US.UTF-8
    export LANGUAGE=en_US.UTF-8
    ```

### Environment Setup
    __Note: 
        This is to prepare a Raspberry Pi device for installation of this package. 
        This is mildly different from a requirements.txt file.__ 

 - Install git and others
    ```bash
    # Install support components
    sudo apt-get install git git-core python3-pip python3-dev python3-pandas python3-mysqldb python3-rpi.gpio
    # Install packages
    sudo pip3 install Adafruit_DHT sqlalchemy 
    # Make directories for storing things
    mkdir data keys logs extras
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


