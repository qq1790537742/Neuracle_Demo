from abc import ABCMeta, abstractmethod
class ProducerInterface(metaclass=ABCMeta):

    @abstractmethod
    def list_topics(self, topic=None, timeout=0.5):
        pass

    @abstractmethod
    def send(self, topic, value, key=None):
        pass

    @abstractmethod
    def close(self):
        pass
