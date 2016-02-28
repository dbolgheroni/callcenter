#!/usr/bin/env python

from __future__ import print_function

from collections import deque
import uuid

from twisted.internet.protocol import Factory
from twisted.internet import reactor, defer
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

        # if a call uuid is detected, proceed to call an operator
        if self.__callid:
            # since lineReceived is called whenever a new line is
            # received, we must save it to not be overridden
            self.__callidsave = self.__callid

            print("call", self.__callidsave, "received")
            self.__process_call_start(self.__callidsave)

        # parse ignored calls
        self.__parse_noanswer(line)

    #### parse methods
    def __parse_callid(self, line):
        # try not to use regex, since it's more complex and slower
        callid = line.split(': ')

        if callid[0] == 'variable_call_uuid':
            return callid[1]

    def __parse_noanswer(self, line):
        if line == '-ERR NO_ANSWER':
            print("call {0} ignored by operator {1}".format(
                    self.__callidsave, self.__op.id))

    #### process calls methods
    def __process_call_start(self, callid):
        # get an operator before processing the call
        d = Operator.get_operator()
        d.addCallback(self.__process_call)

    def __process_call(self, op):
        self.__op = op

        # answer call (stop dialing)
        uuid_answer = "api uuid_answer {0}\n\n".format(self.__callid)
        self.transport.write(uuid_answer)

        # call operator
        # generate uuid in Python, and we can simplify parsing code
        # FreeSWITCH uses uuid version 1
        print("call {0} ringing for operator {1}".format(
                self.__callidsave, self.__op.id))

        u = uuid.uuid1()
        originate = "api originate " \
                "{{origination_uuid={0},originate_timeout=10}}" \
                "sofia/internal/{1}% {1}\n\n".format(u, self.__op.effid)
        self.transport.write(originate)

        #print("call {0} answered by operator {1}"
        #        .format(self.__callidsave, self.__op.id)

    def __parse_disconnect(self, line):
        d = line.split(': ')

        if d[0] == "Content-Disposition":
            if d[1] == "disconnect":
                return True
            else:
                return False

    def __process_call_finish(self):
        if self.__op:
            print("call", self.__callidsave, "finished and operator",
                    self.__op.id, "available")
            Operator.return_operator(self.__op)
        else:
            print("call", self.__callidsave, "finished")


class VulcaFactory(Factory):
    def buildProtocol(self, addr):
        return VulcaProtocol(self)


if __name__ == '__main__':
    #o1 = Operator(id=1, effid=1001)
    #o2 = Operator(id=2, effid=1002)
    #o3 = Operator(id=3, effid=1003)
    o4 = Operator(id=4, effid=1004)

    reactor.listenTCP(5678, VulcaFactory())
    reactor.run()
