from abc import ABCMeta, abstractmethod

class ReceiveImplnterface(metaclass=ABCMeta):

    def __init__(self):
        self.receiverSystemPrepared = None

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def receiver_test_start(self):
        pass
