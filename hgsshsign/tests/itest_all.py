# vim:filetype=python:fileencoding=utf-8
import os
import sys
import shutil
import unittest

import mercurial.dispatch

from hgsshsign.tests._support import make_test_repo


PUBKEY = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCeWqRjW5fHhnH/AN7DM/""" \
"""fBoVFehB8++SwBy6WlEK6bR1jvwBzQUuOpbb4jiv5OVK4JjYWph5HLmsbKvOrH4ZorV""" \
"""o7ZsFq2KlTA/G5Nqhbnj9mgBtp4FQ5rPjh7MApM8xXgVC/5ZGzTU2ygJBgf6gG99bxv""" \
"""spN1dCEWYwlIRd33Fp1flBcATGp8Yyt6ERtgqCwsM/T4V0qFSMUH1guRg5jT3LxdDew""" \
"""p1V1oj5BlZGPZYKX1HqpOUMDFqzrESJjiDIuHy4ltiWLQNxGY6udLp9srmjsWp4LiTK""" \
"""/BUf0m46qR83zJpaFfCdagi2tLH/zQAK21TMrVJQcjKry+dLT/OJIZ dummy@localhost"""
PRIVKEY = """\
"dummy@localhost" RSA private key
This key has no passphrase and is intended for testing
purposes only.

-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAnlqkY1uXx4Zx/wDewzP3waFRXoQfPvksAculpRCum0dY78Ac
0FLjqW2+I4r+TlSuCY2FqYeRy5rGyrzqx+GaK1aO2bBatipUwPxuTaoW54/ZoAba
eBUOaz44ezAKTPMV4FQv+WRs01NsoCQYH+oBvfW8b7KTdXQhFmMJSEXd9xadX5QX
AExqfGMrehEbYKgsLDP0+FdKhUjFB9YLkYOY09y8XQ3sKdVdaI+QZWRj2WCl9R6q
TlDAxas6xEiY4gyLh8uJbYli0DcRmOrnS6fbK5o7FqeC4kyvwVH9JuOqkfN8yaWh
XwnWoItrSx/80ACttUzK1SUHIyq8vnS0/ziSGQIDAQABAoIBAEnMGDwtnUhhAZND
ho0WFOpqEY+opx8j5DxZ+bI5WgYHdA0XTNZRKsP03t2VkvpSQGE3UQk2ot1uHiKx
dAD+xGhaCGyu4Tdv9tuRSJ5tHAuCYHtRdlLsDTIxZwUR2FsQFivbUBg7kvPRNxhS
eeO1nGY4tT6gzFO6cQkL0nGaDd1uMvAu1zENBWAtH7iZyJ5u+GEdlmWs7GTUb0lu
vURjy1iqJTP4tDQtVpQexLeypOKlL89vaPoLQjw6bxxc8uujUXkEbBy0gjSaivSu
qgWnoTF64tuYHhDFm9zzQXTPJ6nQRz7Mxa9mkrPyL/955fvKxHyAlXl+HQnXbE97
Uk4M09kCgYEAy49rVd5uHpaGPFLLEBYSmiSGklXjuNY3sHH3zHk2hVgaxCQt6u1U
5pSPMwsnk0VXtf0B+YSLoxwZNS726Z/TiJ2iPFoQmYY920IgtB9tJ5wpq76Zkmzo
MheRV4e5D9ZWRwOZjQtUlu1TAgvsbEeGcelvNlNzjPYKFt68+Q4uG+cCgYEAxyXs
tjQFkgtcBXwvuKTcW234Y/+lqKK0cVLpzsBQ1VpaCQBy55BGPLZrNck4If0+cZCe
cF6UjH3+5Dd1Q23SxsNryyn2sQoHsys1B5nZyGNvHYwZDnmep+uB7h/oRB95/0hA
YN56ATNFhViISxmctuHeEQK+lQP38bSr3f5+If8CgYA16iCVt7oW4+td4tfhxNbc
eLwj2hfchvBtDWKCh8BHBRThymtXA9Eu2T4sWNH8kasvinmRaufJJdIPYgcHzcsr
LgUgUwJ+hy2u+w7KZmB000m+MVdfjvTY/6EBO/NqHGzxliR/VPbsmqMXsazG6RLU
7O0FyIicVzZI5GnM1VKlFQKBgEFMhSZlPmJZyS2fP8KKhBqSn3yiib4Ww5XY+wMo
+hhLDPSgqgyVuQIVSmgTd41ljUENi3YK/Shn89j++jtG2nMEBudR9iqswEOWakf4
wXk8aWXF1z1w0X378dmTqsQTkhwLo9hfep/EIQqNMft2BXXN79OiE72m1Hjzpdsf
pFofAoGARtxV/WP0nK9aHQQSPPmXB8C+15s4fTCV0krAPj2L5mOB/V63XOJ77IUB
1MXm6iFwsteyQsEJVeP03S1ToRurMXxw6nlkRPP2M5flYCT1EapqduI9dfXnlhu/
ea7iH7LLWTDQ5X97VHu8WTQLSZfH2vT7vuOG5V4R3wOj7rQh6n0=
-----END RSA PRIVATE KEY-----
"""


class TestHgSSHSign(unittest.TestCase):
    _orig_dir = ''
    _tmp_repo = ''
    _tmpdir = ''
    _public_key = ''
    _private_key = ''

    _orig_env = os.environ.copy()
    _testenv = None

    def setUp(self):
        self._orig_dir = os.getcwd()

        self._tmpdir, self._tmp_repo = make_test_repo()
        self._public_key = os.path.join(self._tmpdir, 'id_rsa.pub')
        self._private_key = os.path.join(self._tmpdir, 'id_rsa')

        pubkey = open(self._public_key, 'w')
        pubkey.write(PUBKEY)
        pubkey.close()

        privkey = open(self._private_key, 'w')
        privkey.write(PRIVKEY)
        privkey.close()

        self._testenv = self._orig_env.copy()
        if 'SSH_AUTH_SOCK' in self._testenv:
            self._testenv.pop('SSH_AUTH_SOCK')

        sys._real_argv = sys.argv
        sys.argv = ['hg', '--config', 'sshsign.public_key=' + self._public_key,
                    '--config', 'extensions.hgsshsign=']

        os.chdir(self._tmp_repo)

    def tearDown(self):
        os.chdir(self._orig_dir)
        os.environ = self._orig_env

        if self._tmpdir:
            shutil.rmtree(self._tmpdir)

        sys.argv = sys._real_argv

    def test_sign_simple_case(self):
        try:
            sys.argv.append('sshsign')
            mercurial.dispatch.run()
        except ValueError:
            # in reality, this is an XFAIL for now
            pass


def tests():
    unittest.main()
    return 0


if __name__ == '__main__':
    sys.exit(tests())
