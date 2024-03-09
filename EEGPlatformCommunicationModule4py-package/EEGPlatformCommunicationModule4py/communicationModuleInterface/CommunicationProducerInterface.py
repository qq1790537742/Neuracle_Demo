"""
@File:CommunicationProducerInterface.py
@Author:lcx
@Date:2020/10/714:37
@Desc:
"""
from abc import ABCMeta, abstractmethod
class CommunicationProducerInterface(metaclass=ABCMeta):

    # @abstractmethod
    # def list_topics(self, topic: str = None, timeout: float = 0.5):
    #     """
    #
    #     :param topic: this param is the topic name that you want to inquire, type: str
    #     :param timeout: this param is the inquire timeout, type: int
    #     :return: Map of topics indexed by the topic name. Value is TopicMetadata object in confluent-kafka.
    #     """
    #     pass

    @abstractmethod
    def send(self, topic: str, value: bytes, timeout: float = 1, key=None) -> bool:
        """

        :param topic: this param is the topic name that you want to send message to, type: str
        :param value: this param is the message context, type: bytes
        :param timeout: todo:this param is the timeout for sending a msg, but that doesn't mean the msg sending is failed
        :param key: this param isn't used currently
        :return: True if successfully sent in timeout, False if failed to send in timeout
        """
        pass

    @abstractmethod
    def close(self, timeout: float = 1):
        """

        :param: timeout: this param is the flush timeout before closed
        :return: None
        """
        pass