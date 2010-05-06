# vim: set filencoding=utf8
"""
Key Loader Functions

@author: Mike Crute (mcrute@gmail.com)
@organization: SoftGroup Interactive, Inc.
@date: May 05, 2010
"""

import os
from M2Crypto import RSA, DSA
from M2Crypto.EVP import MessageDigest
from M2Crypto.RSA import RSAError
from M2Crypto.DSA import DSAError
from structutils import unpack_string, get_packed_mp_ints, int_to_bytes


class PublicKey(object):

    def __init__(self, hashed=None, instance=None, key_type=None):
        self.instance = instance
        self.hashed = hashed
        self.key_type = key_type

    @property
    def blob(self):
        return self.hashed.decode('base64')

    def verify(self, data, signature):
        try:
            return bool(self.instance.verify(data, signature))
        except (RSAError, DSAError):
            return False

    def sign(self, data):
        return self.instance.sign(data)

    @classmethod
    def from_string(cls, key):
        """
        Loads an RFC 4716 formatted public key.
        """
        pubkey = cls()

        if key.startswith('ssh-'):
            pubkey.hashed = key.split()[1]
        else:
            pubkey.hashed = key

        pubkey.key_type, remainder = unpack_string(pubkey.blob)

        if pubkey.key_type == 'ssh-rsa':
            e, n = get_packed_mp_ints(remainder, 2)
            pubkey.instance = RSA.new_pub_key((e, n))
        elif pubkey.key_type == 'ssh-dss':
            p, q, g, y = get_packed_mp_ints(remainder, 4)
            pubkey.instance = DSA.set_params(p, q, g)

        return pubkey

    @classmethod
    def from_file(cls, filename):
        fp = open(filename)
        try:
            return cls.from_string(fp.read())
        finally:
            fp.close()


def load_private_key(filename):
    fp = open(filename)
    try:
        first_line = fp.readline()
    finally:
        fp.close()

    type = DSA if 'DSA' in first_line else RSA
    return type.load_key(filename)


def sign_like_agent(data, key):
    """
    Emulates the signing behavior of an ssh key agent.
    """
    digest = MessageDigest('sha1')
    digest.update(data)
    my_data = digest.final()
    return key.sign(data)
