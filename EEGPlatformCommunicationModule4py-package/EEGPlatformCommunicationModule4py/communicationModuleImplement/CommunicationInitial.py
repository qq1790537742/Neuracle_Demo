"""
@File:CommunicationInitial.py
@Author:lcx
@Date:2020/10/714:38
@Desc:
"""
import os
import sys

from ..communicationModuleImplement.componentInterface.queryInterface import QueryInterface

# curPath = os.path.abspath(os.path.dirname(__file__))
# rootPath = os.path.split(curPath)[0]
# sys.path.append(rootPath)
from confluent_kafka.cimpl import KafkaException

from ..communicationModuleInterface.CommunicationInitialInterface import CommunicationInitialInterface
from confluent_kafka.admin import AdminClient, NewTopic
import json
from ..communicationModuleInterface.communicationModuleException import Exceptions


class CommunicationInitial(CommunicationInitialInterface):

    @staticmethod
    def topicQuery(communicationCharactor: QueryInterface):
        """

        :param communicationCharactor: a instance of class "CommunicationConsumer" or "CommunicationProducer"
        :return: a dict of futures for each topic, keyed by the topic name. type: dict(<topic_name, future>)
        """
        try:
            return communicationCharactor.listTopics(communicationCharactor)
        except KafkaException as kafkae:
            raise Exceptions.TopicQueryFailed(kafkae)

    @staticmethod
    def topicCreate(topic: str, confPath: str, num_partitions=1, replication_factor=1):
        """

        :param topic: this param is the name of the topic that you want to create. type: str
        :param confPath: broker configuration, "bootstrap.servers" must be set
        :param num_partitions: this param is the partition number of the topic that you want to create.
        default: 1, type: int
        :param replication_factor: this param is the replication number of the topic that you want to create.
        default: 1, type: int
        :return: a dict of futures for each topic, keyed by the topic name. type: dict(<topic_name, future>)
        """
        if not os.path.exists(confPath):
            raise Exceptions.NoConfigFileException("NoConfigFileException in {}".format(confPath))
        with open(confPath, 'r') as load_f:
            conf = json.load(load_f)
        if not "bootstrap.servers" in conf.keys():
            raise Exceptions.WrongConfigContextException("need bootstrap.servers")
        adminClient = AdminClient(conf)
        new_topics = [NewTopic(topic, num_partitions, replication_factor)]
        fs = adminClient.create_topics(new_topics)
        for topic, f in fs.items():
            try:
                f.result(timeout=1)  # The result itself is None
                return topic
            except KafkaException as ke:
                # topic already exits.
                if ke.args[0].code == 37:
                    return topic
            except Exception as e:
                raise Exceptions.TopicCreateFailed(e)

    @staticmethod
    def topicDelete(topic: str, confPath: str):
        """

        :param topic: this param is the name of the topic that you want to create. type: str
        :param confPath: broker configuration, "bootstrap.servers" must be set
        :return: a dict of futures for each topic, keyed by the topic name. type: dict(<topic_name, future>)
        """
        if not os.path.exists(confPath):
            raise Exceptions.NoConfigFileException
        with open(confPath, 'r') as load_f:
            conf = json.load(load_f)
        if not "bootstrap.servers" in conf.keys():
            raise Exceptions.WrongConfigContextException
        adminClient = AdminClient(conf)
        fs = adminClient.delete_topics([topic], request_timeout=1)
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                return topic
            except Exception as e:
                raise Exceptions.TopicDeleteFailed(e)
