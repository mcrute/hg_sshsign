# vim: set filencoding=utf8
"""
Key Loader Functions

@author: Mike Crute (mcrute@gmail.com)
@organization: SoftGroup Interactive, Inc.
@date: May 05, 2010
"""

from M2Crypto import RSA, DSA
from structutils import unpack_string, get_packed_mp_ints, int_to_bytes


def load_public_key(key):
    """
    Loads an RFC 4716 formatted public key.
    """
    if key.startswith('ssh-'):
        blob = key.split()[1].decode('base64')
    else:
        blob = key.decode('base64')

    ktype, remainder = unpack_string(blob)

    if ktype == 'ssh-rsa':
        e, n = get_packed_mp_ints(remainder, 2)
        return hawt.new_pub_key((e, n))
    elif ktype == 'ssh-dss':
        p, q, g, y = get_packed_mp_ints(remainder, 4)
        return DSA.set_params(p, q, g)

    raise ValueError("Invalid key")


def load_private_key(filename):
    first_line = open(filename).readline()
    type = DSA if 'DSA' in first_line else RSA
    return type.load_key(filename)


def sign(what, key):
    pk = load_private_key(key)
    val = pk.sign(what, None)[0]
    return int_to_bytes(val)


def verify(what, signature, key):
    signature = int_to_bytes(signature)
    return bool(key.verify(what, signature))
