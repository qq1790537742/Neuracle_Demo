"""
@File:CommunicationInitialInterface.py
@Author:lcx
@Date:2020/10/714:37
@Desc:
"""
from abc import ABCMeta, abstractmethod

class CommunicationInitialInterface(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def topicQuery(communicationCharactor):
        pass

    @staticmethod
    @abstractmethod
    def topicCreate(topic: str, confPath: str, num_partitions=1, replication_factor=1):
        pass

    @staticmethod
    @abstractmethod
    def topicDelete(topic: str, confPath: str):
        pass