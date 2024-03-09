import os
import uuid
import time
import pickle
from threading import Thread
from loguru import logger
from Common.event2.EventManager import Event
from EEGPlatformCommunicationModule4py.communicationModuleInterface.communicationModuleException.Exceptions import \
    TopicNotAvailableException
from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationConsumer import CommunicationConsumer


class KafkaConsumer:

    def __init__(self, topic, event_mng):
        # Kafka消费者topic
        self.__topic = topic

        # Kafka配置文件
        cur_path = os.path.dirname(__file__)
        cons_config = os.path.join(cur_path, r'config', r'consumer-config.json')

        # kafka consumer
        # consumer订阅topic
        self.__consumer = CommunicationConsumer(cons_config, str(uuid.uuid1()))
        subscribe_flag = False
        while not subscribe_flag:
            try:
                self.__consumer.subscribe(topic)
            except TopicNotAvailableException:
                time.sleep(0.1)
            else:
                break
        logger.info('Kafka订阅成功，订阅topic：' + topic)

        # 事件管理器
        self.event_mng = event_mng

        # 停止flag
        self.stop_flag = False

        # 接收ExchangeMessage的线程
        self.cons_thread = Thread(target=self.__recv_msg)
        self.cons_thread.setDaemon(True)

    def start(self):
        self.cons_thread.start()
        logger.info('开始从Kafka接收数据')

    def stop(self):
        # 停止接收ExchangeMessage的线程
        self.stop_flag = True
        logger.info('停止从Kafka接收数据')
        # 关闭事件处理
        self.event_mng.stop()
        logger.info('事件管理器停止处理事件')

    def __recv_msg(self):
        try:
            while not self.stop_flag:
                # 从Kafka中接收消息
                cons_msg = self.__consumer.receive()
                if cons_msg:
                    if len(cons_msg) == 4:
                        # 反序列化
                        event_type = cons_msg.decode()
                        # 生成Event事件并放入事件管理器
                        event = Event(event_type)
                        self.event_mng.add_event(event)
                        logger.info('接收到事件，事件类型为：{}'.format(event_type))
                    else:
                        # 反序列化
                        event_type = bytes.decode(cons_msg[0:4], encoding='utf8')
                        event_msg = pickle.loads(cons_msg[4:])
                        # 生成Event事件并放入事件管理器
                        event = Event(event_type)
                        event.message = event_msg
                        self.event_mng.add_event(event)
                        logger.info('接收到事件，事件类型为：{}'.format(event_type))
        except TopicNotAvailableException as e:
            logger.info(e)
