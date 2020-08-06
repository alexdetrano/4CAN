#!/usr/bin/env python3
""" Map CAN IDs between 2 CAN buses"""
import time
import sys
import os
import can
import argparse

__author__ = "adetrano"

suffix = b'DBEEF'



class Listener(can.Listener):
    def __init__(self):
        self.hits = []
        self.msg_map = {}
    def on_message_received(self, msg):
        if b'DBEEF' in msg.data:
            self.hits.append(msg)

    def process_messages(self):
        for msg in self.hits:
            sent_id = [0,0,0]
            # we only want upper 3 nibbles
            sent_id[0] = msg.data[1] & 0x0F         # strip off leading zero
            sent_id[1] = (msg.data[2] & 0xF0) >> 4  # upper byte
            sent_id[2] = (msg.data[2] & 0x0F)       # lower byte
            sent_id = ''.join([hex(x)[2:] for x in sent_id])
            self.msg_map[sent_id] = hex(msg.arbitration_id)[2:]

    def print_messages(self):
        for sent_id, recv_id in self.msg_map:
            print('sent ID: {} recv ID: {:03x}'.format(sent_id, recv_id))

class Bus2Bus:
    def __init__(self, src_bus, dst_bus):
        self.src_bus = can.interface.Bus(src_bus, bustype='socketcan')
        self.dst_bus = can.interface.Bus(dst_bus, bustype='socketcan')
        self.listener = [Listener()][0]
        #self.src_ch = src_bus.channel
        #self.dst_ch = dst_bus.channel

    def send_msgs(self, start_id=0, end_id=0x7ff):
        for id in range(start_id, end_id+1):
            # include the sending ID as part of the payload
            # so we know original sent ID
            prefix = (id).to_bytes(3, byteorder='big')
            payload = prefix + suffix

            # extended_id determines if ID is 29 bits or 7 bits
            msg = can.Message(arbitration_id=id, data=payload, extended_id=False)

            # send message
            print(f'Sending 0x{id:03x}', end='\r')
            self.src_bus.send(msg)
            time.sleep(0.05)

    def process_msgs(self):
        self.listener.process_messages()

    def print_msgs(self):
        self.listener.print_messages()

    def cleanup(self):
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
    #parser.add_argument('--permute', nargs='+', metavar='interface', help='send/receive on all possible interface permutations')

    return parser.parse_args(args)

def main():
    args = parse_args(sys.argv[1:])
    print(args)
    bus2bus = Bus2Bus(args.src, args.dst)
    bus2bus.send_msgs()
    bus2bus.cleanup()




if __name__ == '__main__':
    main()
