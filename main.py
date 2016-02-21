#!/usr/bin/env python

from __future__ import print_function

from twisted.internet.protocol import Factory
from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver


class VulcaProtocol(LineReceiver):
    # by default, protocols.basic.LineReceiver uses b'\r\n' as the
    # default delimiter, so change it
    delimiter = b'\n'

    def __init__(self, factory):
        self.factory = factory

    # override
    def connectionMade(self):
        print("connection made")
        self.transport.write("connect\n\n")

    def connectionLost(self, reason):
        print("connection lost")

    def lineReceived(self, line):
        self.parse_callid(line)

    def parse_callid(self, line):
        # try not to use regex, since it's more complex and slower
        callid = line.split(': ')

        if callid[0] == 'variable_sip_call_id':
            print('call', callid[1], 'received')


class VulcaFactory(Factory):
    def buildProtocol(self, addr):
        return VulcaProtocol(self)


if __name__ == '__main__':
    reactor.listenTCP(5678, VulcaFactory())
    reactor.run()
