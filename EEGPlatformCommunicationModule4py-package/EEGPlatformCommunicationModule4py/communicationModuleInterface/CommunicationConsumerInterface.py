"""
@File:CommunicationConsumerInterface.py
@Author:lcx
@Date:2020/10/714:36
@Desc:
"""
from abc import ABCMeta, abstractmethod
class CommunicationConsumerInterface(metaclass=ABCMeta):

    @abstractmethod
    def subscribe(self, topic: str) -> None:
        """

        :param topic: this param is the topic this consumer need to subscribe
        :return: incoming param "topic" when subscribe successfully
        """
        pass

    @abstractmethod
    def unsubscribe(self) -> None:
        pass

    # @abstractmethod
    # def list_topics(self, topic: str = None, timeout: float = 0.5) -> list:
    #     """
    #
    #     :param topic: this param is the topic name that you want to inquire, type: str
    #     :param timeout: this param is the inquire timeout, type: int
    #     :return: List of topics.
    #     """
    #     pass

    @abstractmethod
    def receive(self) -> bytes:
        """

        :return: unpacking message received in timeout. type: bytes or None(when there is no message in timeout)
        """
        pass

    @abstractmethod
    def timeStampReceive(self) -> list:
        """

        :return: a list of timestamp and message value.
        the first element in the list is a tulpe of timestamp. the first element is timestamp type,
        which is a number in 0, 1 or 2.
        0 means the timestamp isn't available, in this case, the return timestamp should be ignore.
        1 means the return timestamp is the number of milliseconds of the message creation time.
        2 means the return timestamp is the number of milliseconds of the broker receive time.
        the first element in the list is bytes of  message value.
        type: [(int, int), bytes] or None(when there is no message in timeout)
        """
        pass

    @abstractmethod
    def close(self):
        """

        :return: NoneType
        """
        pass