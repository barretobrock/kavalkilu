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



