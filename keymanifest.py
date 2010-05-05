# vim: set filencoding=utf8
"""
Key Manifest

@author: Mike Crute (mcrute@gmail.com)
@organization: SoftGroup Interactive, Inc.
@date: May 05, 2010
"""

from keys import load_public_key


class KeyManifest(dict):
    """
    KeyManifest stores a list of public keys indexed by their
    comment field. This object acts like a dictionary and will
    return public key instances for getitems.
    """

    @classmethod
    def from_file(cls, filename):
        inst = cls()
        fp = open(filename)

        for line in fp:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            _, key, user = line.split()
            inst[user.strip()] = key.strip()

        return inst

    def __getitem__(self, key):
        return load_public_key(dict.__getitem__(self, key))
