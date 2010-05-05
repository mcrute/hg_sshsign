# vim: set filencoding=utf8
"""
Utilities for Manipulating Byte Streams

@author: Mike Crute (mcrute@gmail.com)
@organization: SoftGroup Interactive, Inc.
@date: May 05, 2010
"""

import struct


INT_FORMAT = struct.Struct('>I')


def pack_string(string):
    """
    Pack a string into a network style byte array.
    """
    return pack_int(len(string)) + string


def pack_int(integer):
    """
    Pack an integer into a byte array.
    """
    return INT_FORMAT.pack(integer)


def pack_mp_int(mp_int):
    """
    Pack a multiple-percision integer into a byte array.
    """
    return pack_string(int_to_bytes(mp_int))


def unpack_string(buf):
    """
    Unpack a string from a byte array buffer returning
    the string and the remainder of the buffer.
    """
    length, = INT_FORMAT.unpack(buf[:4])
    string = buf[4:4+length]
    remainder = buf[4+length:]
    return string, remainder


def unpack_mp_int(buf):
    """
    Unpack a multiple-percision integer from a byte array
    buffer returning the string and the remainder of the
    buffer.
    """
    length, = INT_FORMAT.unpack(buf[:4])
    remainder = buf[4+length:]

    return bytes_to_int(buf[4:4+length]), remainder


def unpack_int(buf):
    """
    Unpack an integer from a byte array buffer returning the
    string and the remainder of the buffer.
    """
    integer, = INT_FORMAT.unpack(buf[:4])
    remainder = buf[4:]
    return integer, remainder


def get_packed_mp_ints(buf, count=1):
    """
    Get a number of multiple-percision integers from a byte
    array buffer but leaves them as network style mpints.
    """
    ints = []
    for _ in range(count):
        length, = INT_FORMAT.unpack(buf[:4])
        ints.append(buf[:4+length])
        buf = buf[4+length:]

    return ints


def int_to_bytes(integer):
    """
    Convert an integer or a long integer to an array of
    bytes.
    """
    bytes = []

    while integer > 0:
        integer, chunk = divmod(integer, 256)
        bytes.insert(0, chr(chunk))

    return ''.join(bytes)


def bytes_to_int(buf):
    """
    Convert an array of bytes into an integer or long
    integer.
    """
    integer = 0
    for byte in buf:
        integer <<= 8
        integer += ord(byte)

    return integer
