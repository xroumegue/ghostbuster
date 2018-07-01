#! /usr/bin/env python3
"""
    Implements GhostBuster server: The firehouse !
"""
from logging import getLogger
from socket import socket, timeout, AF_INET, SOCK_STREAM
from struct import pack, unpack, calcsize

class FireHouse():
    """
        GhostBuster's House: Keep the ghost in jail
    """
    def __init__(self, port=12345, listen_addr=''):
        self.port = port
        self.listen_addr = listen_addr
        self.log = getLogger()

        # Create the server
        self.server = socket(AF_INET, SOCK_STREAM)
        self.clf = None

    def set_classifier(self, classifier):
        """
            Set the classifier used by the fire house
        """
        self.clf = classifier

    def start(self):
        """
            Open the jail
        """
        self.log.info("Server listening on {:s}, port {:d}".format(
            self.listen_addr,
            self.port)
                     )

        self.server.bind((self.listen_addr, self.port))
        self.server.listen(1)

        try:
            try_connection = True
            while try_connection:
                self.log.debug("Waiting for a connection")
                self.server.settimeout(30.0)
                (client, address) = self.server.accept()
                self.log.debug("Got a connection from {:s} - {:d}".format(
                    address[0],
                    address[1])
                              )

                keep_connection = True
                while keep_connection:
                    client.settimeout(10.0)
                    try:
                        msg = client.recv(1024)
                        if not msg:
                            self.log.error("Received an empty message")
                            keep_connection = False
                            continue
                        length = unpack("I", msg[:calcsize("I")])[0]
                        if length == 0:
                            self.log.debug("Keep alive packet - no measurement")
                            client.send(pack("I", 0xFF))
                            continue
                        data = unpack("{}f".format(length), msg[calcsize("I"):])
                        self.log.info("Measurement to classify: {}".format(data))
                        rsp = self.clf.classify([data])
                        client.send(pack("I", rsp[0]))
                    except timeout:
                        keep_connection = False
        except timeout:
            try_connection = False

    def stop(self):
        """
            Stop the jail.. are you sure ?..
        """
        self.server.close()
