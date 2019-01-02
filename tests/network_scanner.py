"""
Periodically scans the network for unknown devices.
    If any device found, a record is made.

    Requires:
        sudo apt-get install nmap
        pip3 install python-nmap
"""
from scapy.all import srp, Ether, ARP, conf


conf.verb = 0
ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst='192.168.0.0/24'), timeout=2, inter=0.1)




import nmap


nmap
nm = nmap.PortScanner()
nm.scan(hosts='192.168.1.0/24', arguments='-sn')

guest_list = []

for host in nm.all_hosts():
    host_info = nm[host]
    guest_info = {
        'address': host,
        'name': host_info.hostname(),
    }
    print('=' * 40)
    print('Host:\t {} ({})'.format(host, host_info.hostname()))
    print('State:\t {}'.format(host_info.state()))
    for proto in host_info.all_protocols():
        print('-' * 20)
        print('Protocol:\t {}'.format(proto))
        lport = host_info[proto].keys()
        lport = sorted(list(lport))
        for port in lport:
            print('Port: {}\tstate: {}'.format(port, host_info[proto][port]['state']))


