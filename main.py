#!/usr/bin/env python

from __future__ import print_function

from collections import deque

from twisted.internet.protocol import Factory
from twisted.internet import reactor, threads
from twisted.protocols.basic import LineReceiver

from loperator import *


class VulcaProtocol(LineReceiver):
    # by default, protocols.basic.LineReceiver uses b'\r\n' as the
    # default delimiter, so change it
    delimiter = b'\n'

    def __init__(self, factory):
        self.factory = factory
        self.__callid = None
        self.__op = None

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
        # try to get an operator first
        d = threads.deferToThread(Operator.get_operator)
        d.addCallback(self.__process_call)

    def __process_call(self, op):
        self.__op = op
        print("call", self.__callidsave, "answered by operator", self.__op.id)

    def __parse_disconnect(self, line):
        d = line.split(': ')

        if d[0] == "Content-Disposition":
            if d[1] == "disconnect":
                return True
            else:
                return False

    def __process_call_finish(self):
        if self.__op:
            Operator.return_operator(self.__op)
            print("call", self.__callidsave, "finished and operator",
                    self.__op.id, "available")
        else:
            print("call", self.__callidsave, "finished")


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
