import struct

GIVE_ID = 0x22222222
GIVE_ID_N = 42
CLOSE_CONN = 0x11111111
TAIL_BLOCK = 0b01
FOOD_BLOCK = 0b10


def RecieveHeader(connection):
    return struct.unpack(">ii", connection.recv(8))


def RecieveObjects(connection, n_objs):
    raw_data = connection.recv(4*4*n_objs)
    return struct.unpack(">"+"i"*(n_objs*4), raw_data)


def grouper(iterable, n):
    # *n replicates the iterator so each .next moves "all" the iterators
    return zip(*[iter(iterable)]*n)
