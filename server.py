#!/usr/bin/env python2

import socket
import struct
import random
import signal
import itertools
from threading import Thread

from network_utils import *

from copy import deepcopy

client_states = {}
food = []


def ClientHandler(client):
    # Handshake
    client.setblocking(0)
    try:
        client_id, n_objs = RecieveHeader(client)
        if client_id == GIVE_ID and n_objs == GIVE_ID_N:
            while True:
                new_id = random.randrange(123, 893750)
                # Make sure we don't give out an id more than once
                if not client_states.has_key(new_id):
                    break

            print("Giving out id {%d}"%new_id)
            client.sendall(struct.pack(">i", new_id))
            client_id, n_objs = RecieveHeader(client)
            print(client_id, n_objs)

        while client_id != CLOSE_CONN and NETWORKING_ACTIVE:
            client_states[client_id] = RecieveObjects(client, n_objs)

            # Make a copy of the states just incase another thread tries to do
            # some weird stuff
            states = deepcopy(client_states.items())

            # Send the number of user states we're going to send
            client.sendall(struct.pack(">i", len(states)))
            for client_id_key, state in states:
                state_n = state and len(state) or 0
                header = struct.pack(">ii", client_id_key, state_n)
                if state:
                    data = struct.pack(">"+"i"*state_n*4, *itertools.chain(*state))
                else:
                    data = ""
                client.sendall(header+data)

            client_id, n_objs = RecieveHeader(client)

    except:
        print("Issue communicating with client.")

    finally:
        print("Removing client")
        del client_states[client_id]
        client.close()


s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", 4588))

s.listen(5)

NETWORKING_ACTIVE = True
def SignalHandler(signal, frame):
    global NETWORKING_ACTIVE
    NETWORKING_ACTIVE = False

# Close nicely on ctrl-c
signal.signal(signal.SIGINT, SignalHandler)


while NETWORKING_ACTIVE:
    client, client_addr = s.accept()

    print(client_addr)
    t = Thread(target=ClientHandler, args=(client,))
    t.start()
