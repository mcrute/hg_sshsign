# vim: set filencoding=utf8
"""
SSH Agent Management

@author: Mike Crute (mcrute@gmail.com)
@organization: SoftGroup Interactive, Inc.
@date: May 05, 2010
"""
import os
import socket
import struct

from structutils import int_to_bytes
from structutils import pack_string, pack_int
from structutils import unpack_int, unpack_string, unpack_mp_int


class SSHAgent(object):
    """
    SSH Agent communication protocol for signing only.
    """

    SSH2_AGENT_SIGN_RESPONSE = 14
    SSH2_AGENTC_SIGN_REQUEST = 13

    def __init__(self, socket_path=None):
        default_path = os.environ.get('SSH_AUTH_SOCK')
        socket_path = default_path if not socket_path else socket_path

        if not socket_path:
            raise ValueError("Could not find an ssh agent.")

        self.socket_path = socket_path
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(self.socket_path)

    def _build_packet(self, data, key):
        key = pack_string(key)
        data = pack_string(data)
        flags = pack_int(0)

        to_send = ''.join([chr(SSHAgent.SSH2_AGENTC_SIGN_REQUEST),
                               key, data, flags])
        pkt_length = len(to_send)
        packet = pack_int(pkt_length) + to_send

        return packet

    def sign(self, data, key):
        if not self.socket:
            self.connect()

        packet = self._build_packet(data, key)

        remaining = 0
        while remaining < len(packet):
            sent = self.socket.send(packet[remaining:])
            remaining += sent

        return self._parse_response()

    def _parse_response(self):
        response_length = unpack_int(self.socket.recv(4, socket.MSG_WAITALL))[0]
        if response_length == 1:
            raise ValueError("Agent failed")

        response = self.socket.recv(response_length, socket.MSG_WAITALL)

        status = ord(response[0])
        if status != SSHAgent.SSH2_AGENT_SIGN_RESPONSE:
            raise ValueError("Invalid response from agent")

        _, remainder = unpack_int(response[1:])
        _, remainder = unpack_string(remainder)
        response, _ = unpack_mp_int(remainder)

        return int_to_bytes(response)
