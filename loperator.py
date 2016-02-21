class Operator:
    def __init__(self, id=id, state=0):
        self.__id = id
        self.__state = state

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
