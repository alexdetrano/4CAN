#!/usr/bin/env python3
""" Map CAN IDs between 2 CAN buses"""
import time
import sys
import os
import can
import argparse
import asyncio
from dataclasses import dataclass

__author__ = "adetrano"

suffix = b'DBEEF'
can2hs = {'can0': 0, 
          'can1': 1,
          'can2': 2,
          'can3': 3
}

def autoint(x):
    """Stupid helper function so we can pass in hex values and not have to convert from string"""
    return int(x,0)

# eq=True allows us to make comparisons of instances
# frozen=True creates a __hash__ so we can add it to hashed collections
@dataclass(eq=True, frozen=True)
class MsgMap:
    """Dataclass to store received messages"""
    tx_ch : int
    rx_ch : int
    tx_id : int
    rx_id : int
    difference: int

    def __repr__(self):
        return f'tx_bus={self.tx_ch} rx_bus={self.rx_ch} tx_id=0x{self.tx_id:03x} rx_id=0x{self.rx_id:03x} difference={self.difference}'

class Listener(can.Listener):
    def __init__(self):
        self.hits = []
        self.msg_map = set()

    def on_message_received(self, msg):
        """Callback for whenever a message is received on CAN bus"""
        if suffix in msg.data:
            self.hits.append(msg)

    def process_messages(self):
        """Extract the source ID from received messages"""
        for msg in self.hits:
            tx_ch = (msg.data[0] >> 4) & 0x0f
            rx_ch = msg.data[0] & 0x0f
            
            tx_id = bytearray(3)
            # we only want upper 3 nibbles
            tx_id[0] = msg.data[1] & 0x0F         # strip off leading zero
            tx_id[1] = (msg.data[2] & 0xF0) >> 4  # upper byte
            tx_id[2] = (msg.data[2] & 0x0F)       # lower byte
            tx_id = (tx_id[0] << 8) | (tx_id[1] << 4) | tx_id[0]
            rx_id = msg.arbitration_id
            difference = int(tx_id != rx_id)
            self.msg_map.add(MsgMap(tx_ch, rx_ch, tx_id, rx_id, difference))


    def print_messages(self):
        """Print out received messages"""
        for msg in self.msg_map:
            print(msg)

class Bus2Bus:
    def __init__(self, src_bus, dst_bus, start_id=0x0, end_id=0x7ff, msg_repeat=5, delay=0.1):
        self.src_bus = can.interface.Bus(src_bus, bustype='socketcan')
        self.dst_bus = can.interface.Bus(dst_bus, bustype='socketcan')
        self.listener = Listener()
        self.notifier = can.Notifier(self.dst_bus, [self.listener])
        self.start_id = start_id
        self.end_id = end_id
        self.src_ch = self.src_bus.channel
        self.dst_ch = self.dst_bus.channel
        self.msg_repeat = msg_repeat
        self.delay = delay

    def send_msgs(self):
        """Send encoded messages

           messages encoded as follows:
             msg[0] = {tx_bus, rx_bus} - packed into an char
             msg[1:2] = original arbitration ID
             msg[3:7] = b'DBEEF' - look for these bytes on the RX channel
        """
        bus_prefix = (can2hs[self.src_ch] << 4) | can2hs[self.dst_ch]
        bus_prefix = bus_prefix.to_bytes(1, byteorder='big')
        print(f'Sending messages from {self.src_ch} to {self.dst_ch}', file=sys.stderr)
        for id in range(self.start_id, self.end_id+1):
            # include the sending ID as part of the payload
            # so we know original sent ID
            can_id = (id).to_bytes(2, byteorder='big')
            payload = bus_prefix + can_id + suffix

            # extended_id determines if ID is 29 bits or 7 bits
            msg = can.Message(arbitration_id=id, data=payload, extended_id=False)

            # send message multiple times to ensure our script detects it
            # sometimes sending once causes the script to miss it
            print(f'Sending 0x{id:03x}', end='\r', file=sys.stderr)
            for _ in range(self.msg_repeat):
                self.src_bus.send(msg)
                time.sleep(self.delay)

    def process_msgs(self):
        """Check to see if any messages contain our string"""
        self.listener.process_messages()

    def print_msgs(self):
        """Pretty print any matching messages"""
        self.listener.print_messages()

    def cleanup(self):
        """Gracefully cleanup once we are done"""
        self.listener.stop()
        self.src_bus.shutdown()
        self.dst_bus.shutdown()

def usage():
    script_name = os.path.basename(sys.argv[0])
    print('Usage: {} send_if recv_if'.format(script_name))
    print('eg {} can0 can1'.format(script_name))
    print('requires python-can - install with `pip3 install python-can`')

def parse_args(args):
    parser = argparse.ArgumentParser(description='Test interbus CAN bus connectivity')
    parser.add_argument('src', metavar='src_interface', help='interface to send CAN messages from')
    parser.add_argument('dst', metavar='dst_interface', help='interface to receive CAN messages on')
    parser.add_argument('--start_id', default=0x0,  type=autoint, help='CAN ID to start testing with eg 0x600')
    parser.add_argument('--end_id', default=0x7ff, type=autoint, help='CAN ID to start testing with eg 0x7ff')
    parser.add_argument('--msg_repeat', default=5, type=int, help='Number of times to repeat sending a message')
    parser.add_argument('--delay', default=0.1, type=float, help='Time to wait between sending messages')
    #parser.add_argument('--permute', nargs='+', metavar='interface', help='send/receive on all possible interface permutations')

    return parser.parse_args(args)

def main():
    args = parse_args(sys.argv[1:])
    bus2bus = Bus2Bus(args.src, args.dst, args.start_id, args.end_id, args.msg_repeat, args.delay)
    bus2bus.send_msgs()
    bus2bus.process_msgs()
    bus2bus.print_msgs()
    bus2bus.cleanup()

if __name__ == '__main__':
    main()
