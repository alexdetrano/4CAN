#!/bin/bash
set -e
modprobe can-gw
echo "flushing existing cangw rules"
cangw -F

echo "bridging can0 <--> can1"
cangw -A -s can0 -d can1
cangw -A -s can1 -d can0

echo "bridging can2 <--> can3"
cangw -A -s can2 -d can3
cangw -A -s can3 -d can2

echo "new cangw rules:"
cangw -L

