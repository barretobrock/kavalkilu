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
sudo apt install build-essential curl git git-core python3-pip python3-dev python3-pandas python3-mysqldb chromium-chromedriver
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

## Future Plans?
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



