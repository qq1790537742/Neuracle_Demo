from abc import ABCMeta, abstractmethod

class ConsumerInterface(metaclass=ABCMeta):
    @abstractmethod
    def subscribe(self, topic):
        pass

    @abstractmethod
    def unsubscribe(self):
        pass

    @abstractmethod
    def list_topics(self, topic=None, timeout=0.5):
        pass

    @abstractmethod
    def receive(self):
        pass

    @abstractmethod
    def close(self, instance):
        pass