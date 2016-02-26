import time
from collections import deque
from twisted.internet import defer

class Operator:
    availableq = defer.DeferredQueue()

    # when added, operator is free
    def __init__(self, id=id, state=0):
        self.__id = id
        self.__state = state
        Operator.availableq.put(self)

    @classmethod
    def get_operator(cls):
        return Operator.availableq.get()

    @classmethod
    def return_operator(cls, op):
        Operator.availableq.put(op)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id
