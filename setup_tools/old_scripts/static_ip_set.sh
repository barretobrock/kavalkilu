#!/usr/bin/env bash
# Sets static IP

if [ "$1" == "reset" ] ; then
    mv /etc/network/interfaces.reset /etc/network/interfaces
    echo "Reset Successfully"
else
    # Get gateway
    gateway=`route -n | grep 'UG[ \t]' | awk '{print $2}'`
    # Get interface (wlan0, eth0, etc.)
    iface=`route -n | grep 'UG[ \t]' | awk '{print $8}'`
    # Get address, broadcast, and netmask
    iln=`ifconfig $iface | grep inet\ addr`

    for i in $iln ; do
        if [ "${i:0:5}" == "addr:" ] ; then
            iaddr=${i:5}
        elif [ "${i:0:6}" == "Bcast:" ] ; then
            bcast=${i:6}
        elif [ "${i:0:5}" == "Mask:" ] ; then
            mask=${i:5}
        fi
    done

    # Get network
    network=`/sbin/route -n | grep $iface | grep $mask | grep -v ^0 | awk '{print $1}'`

    # Save current interface setup as backup
    mv -n /etc/network/interfaces /etc/network/interfaces.reset
    cat /etc/network/interfaces.reset | while read line ; do
        if [ "$line" != "# The loopback network interface" ] && [ -z $d ] ; then
            echo $line >> /etc/network/interfaces
            continue
        elif [ "$line" == "# The loopback network interface" ] ; then
            d=1
            echo $line >> /etc/network/interfaces
            continue
        elif [ "${line:0:2}" != "# " ] && [ $d -eq 1 ] ; then
            d=2
            echo "
    auto lo $iface
    iface lo inet loopback
    iface $iface inet static
        address $iaddr
        netmask $mask
        gateway $gateway
        network $network
        broadcast $bcast" >> /etc/network/interfaces
        elif [ "${line:0:2}" == "# " ] && [ $d -eq 2 ] ; then
            d=3
            echo $line >> /etc/network/interfaces
        elif [ $d -eq 3 ] ; then
            echo $line >> /etc/network/interfaces
        fi
    done
    /etc/init.d/networking restart
    echo "Static IP set done!"
fi



