from abc import ABCMeta, abstractmethod


class ProblemInterface(metaclass=ABCMeta):
    def __init__(self):
        pass
    @abstractmethod
    def getData(self):
        pass

    @abstractmethod
    def report(self,reportModel):
        pass
