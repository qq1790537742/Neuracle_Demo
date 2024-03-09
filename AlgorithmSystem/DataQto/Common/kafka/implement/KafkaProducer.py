from confluent_kafka import Producer
import os
import json
from Common.kafka.exception.exception import *


class KafkaProducer():

    conf = dict()
    topic = ""
    producer = ""
    def __init__(self, confPath, topic=0):
        """

        :param confPath: this param is the path of the producer config file that you want to use. type: str
        :param topic: this param don't need to config
        """
        if not os.path.exists(confPath):
            raise NoConfigFileException
        with open(confPath, 'r') as load_f:
            self.conf = json.load(load_f)
        self.topic = topic
        self.producer = Producer(self.conf)
        # # topic存在保证
        # CommunicationInitial

        # self.consumer.subscribe(self.topic)

    def list_topics(self, topic=None, timeout=0.5):
        """

        :param topic: this param is the topic name that you want to inquire, type: str
        :param timeout: this param is the inquire timeout, type: int
        :return: Map of topics indexed by the topic name. Value is TopicMetadata object in confluent-kafka.
        """
        resultClusterMetadata = self.producer.list_topics(topic, timeout)
        return resultClusterMetadata.topics

    def send(self, topic, value, key=None):
        """

        :param topic: this param is the topic name that you want to send message to, type: str
        :param value: this param is the message context, type: bytes
        :param key: this param isn't used currently
        :return: "ok" if successfully sent
        """
        if not type(value) == type(b"a"):
            raise WrongMessageValueType(type(value))
        else:
            self.producer.produce(topic, value, key)
            self.producer.flush()
            return "ok"

    def close(self):
        """

        :return: None
        """
        self.producer.flush()