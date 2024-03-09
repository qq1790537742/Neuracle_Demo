import os
from loguru import logger
from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationProducer import CommunicationProducer
from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationInitial import CommunicationInitial


class KafkaProducer:
    def __init__(self, topic):
        # Kafka生产者topic
        self.__topic = topic

        # Kafka配置文件
        cur_path = os.path.dirname(__file__)
        prod_config = os.path.join(cur_path, r'config', r'producer-config.json')
        init_config = os.path.join(cur_path, r'config', r'Initial-config.json')

        # 创建topic
        create_result = CommunicationInitial.topicCreate(topic, init_config)

        # kafka producer
        self.__producer = CommunicationProducer(prod_config)

    def send(self, message):
        """
        kafka发送的message要求是bytes格式,如果输入是str格式,则需要先进行encode再发送
        :param message: 需要发送的消息
        """
        if isinstance(message, str):
            message = message.encode()
        if isinstance(message, bytes):
            # 发送bytes格式的message
            send_suc_flag = False
            while not send_suc_flag:
                send_suc_flag = self.__producer.send(self.__topic, message)
            # print(f'发送信息:{message} !' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            logger.info(f'向{self.__topic}发送信息:{message}')
        else:
            raise TypeError('message输入:{}不是bytes或者str类型', message)
