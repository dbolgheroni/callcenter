from collections import deque

class Operator:
    freeopq = deque()
    busyopq = deque()

    # when added, operator is free
    def __init__(self, id=id, state=0):
        self.__id = id
        self.__state = state
        Operator.freeopq.append(self)

    @classmethod
    def get_operator(cls):
        try:
            op = Operator.freeopq.popleft()
        except IndexError:
            return None

        Operator.busyopq.append(op)
        return op

    @classmethod
    def return_operator(cls, op):
        Operator.freeopq.append(op)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id
