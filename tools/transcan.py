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



def usage():
    script_name = os.path.basename(sys.argv[0])
    print('Usage: {} send_if recv_if'.format(script_name))
    print('eg {} can0 can1'.format(script_name))

def main(can_if_send, can_if_recv):
    bus_send = can.interface.Bus(can_if_send, bustype='socketcan')
    bus_recv = can.interface.Bus(can_if_recv, bustype='socketcan')
    listener = [Listener()]  # needs to be an iterable
    #notifier = can.Notifier(bus_recv, listener)

    max_can_id =  0x7ff

    for id in range(0, max_can_id):
        # include the sending ID as part of the payload
        # so we know original sent ID
        #prefix = (int.from_bytes(b'000', byteorder='big') | id).to_bytes(3, byteorder='big')
        prefix = (id).to_bytes(3, byteorder='big')
        payload = prefix + suffix

        # extended_id determines if ID is 29 bits or 7 bits
        msg = can.Message(arbitration_id=id, data=payload, extended_id=False)

        # send message
        bus_send.send(msg)
        time.sleep(0.1)

    listener[0].process_messages()
    listener[0].print_messages()


if __name__ == '__main__':
    # TOdo: add argparse and start/stop IDs
    if len(sys.argv) < 3:
        usage()
    else:
        main(sys.argv[1], sys.argv[2])
