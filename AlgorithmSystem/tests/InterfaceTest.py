from abc import ABCMeta, abstractmethod


class Test(metaclass=ABCMeta):
    def __init__(self):
        self.tag = None

    @abstractmethod
    def run(self):
        pass

    def print_test(self):
        pass

