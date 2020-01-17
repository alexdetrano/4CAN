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
cat << EOF >> /boot/config.txt
# 4CAN setup
# the order of the interfaces matter
# ie can3,can2,can1,can0 must be preserved
# otherwise can0 will not REALLY be can0
dtparam=spi=on
dtoverlay=spi1-2cs

dtoverlay=mcp2515-can3,oscillator=16000000,interrupt=24
dtoverlay=mcp2515-can2,oscillator=16000000,interrupt=23
dtoverlay=mcp2515-can1,oscillator=16000000,interrupt=25
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=22


# enable uart
enable_uart=1
EOF

#3) reboot
echo "done"
echo "reboot and run 4can.sh to bring up the interfaces"


