#!/bin/sh
ip link set can0 down
ip link set can1 down
ip link set can2 down
ip link set can3 down

ip link set can0 up type can bitrate 500000
ip link set can1 up type can bitrate 500000
ip link set can2 up type can bitrate 500000
ip link set can3 up type can bitrate 500000

ip link set can0 txqueuelen 10000
ip link set can1 txqueuelen 10000
ip link set can2 txqueuelen 10000
ip link set can3 txqueuelen 10000
