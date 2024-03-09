import os
from confluent_kafka import Consumer
from Common.kafka.exception.exception import *
import json



class KafkaConsumer():

    conf = dict()
    topic = ""
    consumer = ""
    def __init__(self, confPath, consumerId, topic=0):
        """

        :param confPath: this param is the path of the producer config file that you want to use. type: str
        :param consumerId: this param should be unique in the system, UUID suggested. type: str
        :param topic: this param is the topic this consumer need to subscribe
        """
        if not os.path.exists(confPath):
            raise NoConfigFileException
        with open(confPath, 'r') as load_f:
            self.conf = json.load(load_f)
        self.topic = topic
        self.conf["group.id"] = str(consumerId)
        self.consumer = Consumer(self.conf)
        # # topic存在保证
        # CommunicationInitial

        self.subscribe(self.topic)

    def subscribe(self, topic):
        """

        :param topic: this param is the topic this consumer need to subscribe
        :return: incoming param "topic" when subscribe successfully
        """
        self.consumer.subscribe([topic])
        msg = self.receive()
        if msg:
            msg = str(msg, encoding='utf-8')
            if "Subscribed topic not available" in msg:
                raise TopicNotAvailableException(msg)
            else:
                return topic
        else:
            return topic

    def unsubscribe(self):
        self.consumer.unsubscribe()

    def list_topics(self, topic=None, timeout=0.5):
        """

        :param topic: this param is the topic name that you want to inquire, type: str
        :param timeout: this param is the inquire timeout, type: int
        :return: Map of topics indexed by the topic name. Value is TopicMetadata object in confluent-kafka.
        """
        resultClusterMetadata = self.consumer.list_topics(topic, timeout)
        return resultClusterMetadata.topics

    def receive(self):
        """

        :return: unpacking message received in timeout. type: bytes or None(when there is no message in timeout)
        """
        msg = self.consumer.poll(timeout=0.5)
        if msg:
            return msg.value()
        else:
            return None

    def close(self):
        """

        :return: NoneType
        """
        self.unsubscribe()
        self.close()