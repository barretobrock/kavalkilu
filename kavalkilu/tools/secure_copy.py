#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import paramiko


class FileSCP:
    """
    Establishes a connection for securely copying files from computer to computer.
    Args for __init__:
        privatekey_path: path to privatekey (in "~/.ssh/id_rsa")
        server_ip: Local ip address for home server computer
        server_hostname: Home server's hostname
    Note:
        privatekey has to be generated through this command:
            ssh-keygen -t rsa -C <USERNAME>@<HOSTNAME> OR
            ssh-keygen -t rsa -C "SOMETHING EASIER TO REMEMBER"
            Then press <Enter> 2x
            Then copy id_rsa.pub file to target computer
            cat ~/.ssh/id_rsa.pub | ssh <USERNAME>@<IP-ADDRESS> 'cat >> .ssh/authorized_keys'
    """
    def __init__(self, privatekey_path, server_ip, server_hostname):

        mkey = paramiko.RSAKey.from_private_key_file(privatekey_path)

        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to server using private key
        self.ssh.connect(server_ip, username=server_hostname, pkey=mkey)
        self.sftp = self.ssh.open_sftp()

    def scp_transfer(self, source_path, dest_path, is_remove_file=False):
        """
        Securely copy a file form source to destination
        Args:
            source_path: path of file to be copied
            dest_path: path to file's destination
            is_remove_file: bool, whether to remove the file from source after copy
                default: False
        """
        self.sftp.put(source_path, dest_path)
        if is_remove_file:
            # Try to remove file after successful transfer
            os.remove(source_path)

