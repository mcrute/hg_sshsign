# vim: set filencoding=utf8
"""
SSH Key Signing

@author: Mike Crute (mcrute@ag.com)
@organization: American Greetings Interactive
@date: May 03, 2010

Commands to sign and verify revisions with your
ssh key.
"""

from structutils import bytes_to_int
from sshagent import SSHAgent

key = open('/Users/mcrute/.ssh/id_rsa.ag.pub').read()
key = key.split()[1].decode('base64')

agent = SSHAgent()
signature = agent.sign("Hello world!", key)
print bytes_to_int(signature)
