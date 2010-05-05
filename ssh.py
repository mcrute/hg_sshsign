# vim: set filencoding=utf8
"""
SSH Key Signing

@author: Mike Crute (mcrute@ag.com)
@organization: American Greetings Interactive
@date: May 03, 2010

Commands to sign and verify revisions with your
ssh key.

Ponder this, bitches:
    http://www.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/ssh-rsa.c
    http://svn.osafoundation.org/m2crypto/trunk/SWIG/_rsa.i
"""

from M2Crypto.RSA import RSAError

from structutils import bytes_to_int
from sshagent import SSHAgent
from keys import load_private_key, load_public_key

test_data = "Hello world!"
public_key = "/Users/mcrute/.ssh/id_rsa.ag.pub"
private_key = "/Users/mcrute/.ssh/id_rsa.ag"

key = open(public_key).read()
key = key.split()[1].decode('base64')

agent = SSHAgent()
signature = agent.sign(test_data, key)
print bytes_to_int(signature)


try:
    pub_key = load_public_key(open(public_key).read())
    pub_key.verify(test_data, signature)
    print "Signature matches"
except RSAError:
    print "Signature doesn't match"

priv_key = load_private_key(private_key)
print bytes_to_int(priv_key.sign(test_data))
