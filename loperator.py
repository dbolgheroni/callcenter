from collections import deque

class Operator:
    freeopq = deque()
    busyopq = deque()

    # state 0 is free; state 1 is busy
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

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        self.__state = state
