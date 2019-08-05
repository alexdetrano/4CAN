#!/bin/bash
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

#1) Copy the 4 mcp2515-canx.dtbo files to /boot/overlays
echo "backing up mcp2515 overlays in /boot/overlays to /boot/overlays/bak"
sudo mkdir -p /boot/overlays/bak
sudo cp /boot/overlays/mcp2515* /boot/overlays/bak

echo "copying new overlays into /boot/overlays"
sudo cp ./dtbo/*.dtbo /boot/overlays

#2) copy config.txt to /boot/config.txt (make a backup of original /boot/config.txt just incase)
echo "backing up config.txt to /boot/config.txt.bak"
sudo cp /boot/config.txt /boot/config.txt.bak

echo "modifying /boot/config.txt"
sudo cp config.txt /boot/config.txt

#3) reboot
echo "done"
echo "reboot and run 4can.sh to bring up the interfaces"


