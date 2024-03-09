from abc import ABCMeta, abstractmethod

class InitialInterface(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def topicQuery(communicationCharactor):
        pass

    @staticmethod
    @abstractmethod
    def topicCreate(topic, confPath, num_partitions=1, replication_factor=1):
        pass

    @staticmethod
    @abstractmethod
    def topicDelete(topic, confPath):
        pass