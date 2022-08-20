# kavalkilu
Home Automation Scripts for both server & clients

_This package has been refactored to function as a repository for all methods & scripts that can be run on either a server environment (Ubuntu 18.04+) or a Raspberry Pi client. As such, the methods included should be able to run on a majority of the expected platforms. The main focus of these scripts is in home automation protocols._

## Installation
```bash
python3 -m pip install git+https://github.com/barretobrock/kavalkilu.git
```

## Update
```bash
python3 -m pip install git+https://github.com/barretobrock/kavalkilu.git --upgrade
```

## Testing
 1. Commits on the `develop` branch
 2. `checkout` the develop branch, perform tests.
 3. `merge` `develop` with `master` (asuming all went well.)

## Setup
### Primary machine (server, development env) setup
#### Environment Setup
```bash
sudo apt install build-essential curl git python3-pip python3-dev python3-pandas chromium-chromedriver
```
#### Git setup
We'll want to set up SSH for this machine
1. [Generate an SSH key](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
2. [Add it to GitHub](https://help.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account)
3. Either:
    a. clone new repos locally using SSH
    b. change the remote for already-cloned repos (check with `git remote -v`):
        - Enter the following in the repo:
            `git remote set-url origin git@github.com:barretobrock/kavalkilu.git`
        - Check with `git pull`

## Troubleshooting
### git
 - After git account setup, still prompting for passphrase
    `ssh-add ~/.ssh/id_rsa`
    - Long term fix: Add the following to `~/.bashrc`
```bash
if [[ ! -S ~/.ssh/ssh_auth_sock ]]; then
  eval `ssh-agent`
  ln -sf "${SSH_AUTH_SOCK}" ~/.ssh/ssh_auth_sock
fi
export SSH_AUTH_SOCK=~/.ssh/ssh_auth_sock
ssh-add -l > /dev/null || ssh-add
```
### python
 - python calling dist-packages version
 (better instructions to come.)
 `sudo pip3 install --target=/usr/local/lib/python3.6/dist-packages git+https://github.com/barretobrock/kavalkilu.git#egg=kavalkilu --upgrade`
### crontab
 - Debugging from crontab
    `tail -f /var/log/syslog`

### Chromedriver
 - "This version.... only supports version xx"
    - It seems like chromedriver automatically updated the minimum allowed version of Chrome to run with it. To fix this, you'll typically just have to run `sudo apt update && sudo apt upgrade` to update Chrome to the latest version. `sudo apt list --upgradeable` can help verify the your Chrome version will change

## Tips
 - TBA!
