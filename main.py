#!/usr/bin/env python

from __future__ import print_function

from collections import deque

from twisted.internet.protocol import Factory
from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver

from loperator import *


class VulcaProtocol(LineReceiver):
    # by default, protocols.basic.LineReceiver uses b'\r\n' as the
    # default delimiter, so change it
    delimiter = b'\n'

    def __init__(self, factory):
        self.factory = factory
        self.__callid = None

    # override
    def connectionMade(self):
        #print("connection made")
        # receive
        self.transport.write("connect\n\n")

    def connectionLost(self, reason):
        print("connection lost")

    def lineReceived(self, line):
        # parse call uuid
        self.__callid = self.__parse_callid(line)

        # when a call uuid is detected, try to get an operator
        if self.__callid:
            print("call", self.__callid, "received")

            # add call to queue
            callq.append(self.__callid)
            print("call", self.__callid, "waiting in queue")

            # get an operator
            op = Operator.get_operator()
            if op:
                print("call", self.__callid, "answered by operator",
                        op.id)

                # if there is an operator, call is popped from queue
                callq.popleft()
            else:
                print("all operators are busy")

    def __parse_callid(self, line):
        # try not to use regex, since it's more complex and slower
        callid = line.split(': ')

        if callid[0] == 'variable_call_uuid':
            return callid[1]


class VulcaFactory(Factory):
    def buildProtocol(self, addr):
        return VulcaProtocol(self)


if __name__ == '__main__':
    o1 = Operator(id=0)
    o2 = Operator(id=1)

    # it's a common idiom to use deque() as a queue
    callq = deque()

    reactor.listenTCP(5678, VulcaFactory())
    reactor.run()
