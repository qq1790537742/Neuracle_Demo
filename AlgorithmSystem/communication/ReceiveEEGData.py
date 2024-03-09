import threading
import time
import uuid
import os
import numpy as np
from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationConsumer import CommunicationConsumer
from EEGPlatformCommunicationModule4py.communicationModuleInterface.communicationModuleException.Exceptions import \
    TopicNotAvailableException
import logging


# 从采集端topic接收数据
class ReceiveEEGData(threading.Thread):
    def __init__(self, topic, algo_sys_mng, channel_num, sample_num):
        super().__init__()
        # 接收的topic
        self.topic = topic
        # 接收数据的通道数
        self.channel_num = channel_num
        # 接收数据的采样点
        self.sample_num = sample_num
        # AlgorithmSystemManager实例
        self.algo_sys_mng = algo_sys_mng
        # 是否停止接收数据flag
        self.stop_flag = False
        # 配置文件地址
        cur_path = os.path.dirname(__file__)
        self.config_path = os.path.join(os.path.join(cur_path, r"../communication/config"), 'consumer-config.json')
        # 获得消费者实例
        # 该构造方法的第二个参数为消费者组名，本项目内约定，非特殊声明时，消费者组名应与消费者实例一一对应，即不允许多个消费者使用同一消费者组名
        # 使用者可用UUID之类的唯一标识符做消费者组名
        self.consumer = CommunicationConsumer(self.config_path, str(uuid.uuid1()))
        self.consumer.subscribe(self.topic)

    # 线程的start函数调用此函数？

    def run(self):
        try:
            # 循环接收消息
            while not self.stop_flag:
                consume_msg = self.consumer.receive()
                if consume_msg:
                    data = np.frombuffer(consume_msg, dtype=np.float_)
                    data = data.reshape(self.channel_num, self.sample_num)
                    self.algo_sys_mng.add_data(data)
        except TopicNotAvailableException as e:
            print(e)

    def stop(self):
        self.stop_flag=True