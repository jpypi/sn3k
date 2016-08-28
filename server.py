#!/usr/bin/env python2

import socket
import struct
import random
import itertools
from threading import Thread

from network_utils import *


client_states = {}


def ClientHandler(client):
    # Handshake
    client_id, n_objs = RecieveHeader(client)
    if client_id == GIVE_ID and n_objs == GIVE_ID_N:
        new_id = random.randrange(123, 893750)
        print("Giving out id {%d}"%new_id)
        client.sendall(struct.pack(">i", new_id))
        client_id, n_objs = RecieveHeader(client)

    while client_id != CLOSE_CONN:
        values = RecieveObjects(client, n_objs)
        client_states[client_id] = grouper(values, 4)

        # Send the number of user states we're going to send
        client.sendall(struct.pack(">i", len(client_states)))
        for client_id_key, state in client_states.iteritems():
            header = struct.pack(">ii", client_id_key, len(state))
            data = struct.pack(">"+"i"*len(state)*4, *itertools.chain(*state))
            client.sendall(header+data)

        client_id, n_objs = RecieveHeader(client)

    client.close()


s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", 4588))

s.listen(5)

while True:
    client, client_addr = s.accept()

    print(client_addr)
    t = Thread(target=ClientHandler, args=(client,))
    t.start()
