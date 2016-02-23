#!/usr/bin/env python

from __future__ import print_function

from collections import deque

from twisted.internet.protocol import Factory
from twisted.internet import reactor, protocol, defer
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
        # receive the call
        self.transport.write("connect\n\n")

    def connectionLost(self, reason):
        self.__process_call_finish()

    def lineReceived(self, line):
        # parse call uuid
        self.__callid = self.__parse_callid(line)

        if self.__callid:
            # since lineReceived is called whenever a new line is
            # received, we must save it to not be overridden
            self.__callidsave = self.__callid

            print("call", self.__callidsave, "received")
            self.__process_call_start(self.__callidsave)

    def __parse_callid(self, line):
        # try not to use regex, since it's more complex and slower
        callid = line.split(': ')

        if callid[0] == 'variable_call_uuid':
            return callid[1]

    def __process_call_start(self, callid):
        # get an operator
        self.__op = Operator.get_operator()
        if self.__op:
            print("call", callid, "answered by operator", self.__op.id)
        else:
            # not enough operators, append it to a queue
            callq.append(callid)
            print("call", callid, "waiting in queue")

    def __parse_disconnect(self, line):
        d = line.split(': ')

        if d[0] == "Content-Disposition":
            if d[1] == "disconnect":
                return True
            else:
                return False

    def __process_call_finish(self):
        Operator.return_operator(self.__op)
        print("call", self.__callidsave, "finished and operator",
                self.__op.id, "available")


class VulcaFactory(Factory):
    def buildProtocol(self, addr):
        return VulcaProtocol(self)


if __name__ == '__main__':
    o1 = Operator(id=1)
    o2 = Operator(id=2)

    # it's a common idiom to use deque() as a queue
    callq = deque()

    reactor.listenTCP(5678, VulcaFactory())
    reactor.run()
