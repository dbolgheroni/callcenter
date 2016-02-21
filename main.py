#!/usr/bin/env python

from __future__ import print_function

from twisted.internet.protocol import Factory
from twisted.internet import reactor, protocol

class VulcaProtocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory

    # override
    def connectionMade(self):
        print("connection made")
        self.transport.write("connect\n\n")

    def connectionLost(self, reason):
        print("connection lost")

    def dataReceived(self, data):
        print("#### data received")


class VulcaFactory(Factory):
    def buildProtocol(self, addr):
        return VulcaProtocol(self)

reactor.listenTCP(5678, VulcaFactory())
reactor.run()
