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
 - First time building a proper package, so there's a lot that might go wrong. 
    - Currently, there's an issue with the package not updating when using `pip`.
        To bypass this, I copy the contents of the package directory to the 
        package location in `site-packages`:
        `sudo cp -r ~/kavalkilu ~/.local/lib/python3.6/site-packages`

## Tips


### Initial Pi Setup
    __Note: 
        This is to prepare a Raspberry Pi device for installation of this package. 
        This is mildly different from a requirements.txt file.__ 

 - Install git and others
    `sudo apt-get install git git-core python3-pip python3-dev Adafruit_DHT`
 - Install wiringPi
    ```bash
    # Go home
    cd
    # Make an "extras" folder to hold other packages we'll install
    mkdir extras
    cd extras
    # Clone in WiringPi
    git clone git://git.drogon.net/wiringPi
    cd wiringPi
    # Build the file
    ./build
    ```


