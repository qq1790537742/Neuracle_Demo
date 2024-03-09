"""
@File:CommunicationConsumer.py
@Author:lcx
@Date:2020/10/714:34
@Desc:
"""
import logging
import os
import sys
import time

from confluent_kafka.cimpl import KafkaException

from ..communicationModuleImplement.componentInterface.queryInterface import QueryInterface

from ..communicationModuleInterface.CommunicationConsumerInterface import CommunicationConsumerInterface
from confluent_kafka import Consumer
from ..communicationModuleInterface.communicationModuleException.Exceptions import *
import json

class CommunicationConsumer(CommunicationConsumerInterface, QueryInterface):

    conf = dict()
    topic = ""
    consumer = ""
    def __init__(self, confPath: str, consumerId: str):
        """

        :param confPath: this param is the path of the producer config file that you want to use. type: str
        :param consumerId: this param should be unique in the system, UUID suggested. type: str
        :param topic: this param is the topic this consumer need to subscribe
        """
        self.logger = logging.getLogger("communicationConsumer-{}".format(consumerId))
        self.logger.info("start initial consumer")
        self.retryLimit = None
        self.consumerId = None
        if not os.path.exists(confPath):
            self.logger.fatal("no config file at {}".format(confPath))
            raise NoConfigFileException("no config file at {}".format(confPath))
        with open(confPath, 'r') as load_f:
            self.conf = json.load(load_f)
        self.topic: str = None
        if "retryLimit" in self.conf.keys():
            self.retryLimit = int(self.conf["retryLimit"])
            self.conf.pop("retryLimit")
            self.logger.info("get configuration: retryLimit = {}".format(self.retryLimit))
        self.conf["group.id"] = consumerId
        self.consumerId = consumerId
        self.consumer = Consumer(self.conf)
        self.logger.info("consumer instance built: id={}, config={}, config at: {}".format(consumerId,
                                                                                           str(self.conf), confPath))

    def subscribe(self, topic: str) -> None:
        if topic not in self.listTopics():
            self.logger.fatal("no topic named {}".format(topic))
            raise TopicNotAvailableException("no topic named {}".format(topic))
        self.consumer.subscribe([topic])
        self.topic = topic
        self.logger.info("subscribed topic: {}".format(self.topic))

    def unsubscribe(self) -> None:
        self.consumer.unsubscribe()
        topic = self.topic
        self.topic = None
        self.logger.info("unsubscribed topic: {}".format(topic))

    # todo:给出返回值类型
    def listTopics(self, topic=None, timeout=0.5, retryLimit = 1) -> list:
        result = None
        if self.retryLimit != None:
            retryLimit = self.retryLimit
        else:
            retryLimit = retryLimit
        retryTime = 0
        while retryTime < retryLimit:
            try:
                resultClusterMetadata = self.consumer.list_topics(topic, timeout)
            except KafkaException as ke:
                retryTime += 1
                self.logger.error("get topic list failed, retry for {} time".format(str(retryTime)))
                time.sleep(1)
            else:
                result = list(resultClusterMetadata.topics.keys())
                self.logger.info("get topic list: {}".format(str(result)))
                break
        if result == None:
            self.logger.fatal("topic list query failed, retried {} times, waited for {} secs, found broker not "
                              "available, please check the connection.".format(str(retryLimit), str(retryLimit*1.5)))
            raise TopicQueryFailed("topic list query failed, retried {} times, waited for {} secs, found broker not "
                                   "available, please check the connection.".format(str(retryLimit), str(retryLimit*1.5)))
        return result

    def receive(self) -> bytes:
        if self.topic == None:
            raise NoSubscribeException()
        msg = self.consumer.poll(timeout=0.1)
        if msg:
            self.logger.debug("received a message")
            return msg.value()
        else:
            return None

    def timeStampReceive(self) -> list:
        if self.topic == None:
            raise NoSubscribeException()
        msg = self.consumer.poll(timeout=0.1)
        if msg:
            self.logger.debug("received a timeStamp message")
            return [msg.timestamp(), msg.value()]
        else:
            return None

    def close(self):
        self.unsubscribe()
        self.consumer.close()
        self.logger.info("consumer instance closed: id={}".format(self.consumerId))