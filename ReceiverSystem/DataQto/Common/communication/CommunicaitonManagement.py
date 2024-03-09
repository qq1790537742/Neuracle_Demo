
import queue
import uuid
from threading import Thread
# from Common.communication.operate_message import operate_message_fcn
# from Common.communication.receive_message import receive_message_fcn
# from Common.kafka.implement.KafkaConsumer import KafkaConsumer
# from Common.kafka.implement.KafkaInitial import KafkaInitial
# from Common.kafka.implement.KafkaProducer import KafkaProducer
from ReceiverSystem.DataQto.Common.communication.operate_message import operate_message_fcn
from ReceiverSystem.DataQto.Common.communication.receive_message import receive_message_fcn
from ReceiverSystem.DataQto.Common.kafka.implement.KafkaConsumer import KafkaConsumer
from ReceiverSystem.DataQto.Common.kafka.implement.KafkaInitial import KafkaInitial
from ReceiverSystem.DataQto.Common.kafka.implement.KafkaProducer import KafkaProducer
producer_config_path= r"./Common/kafka/configuration/producer-config.json"
consumer_config_path= r"./Common/kafka/configuration/consumer-config.json"

class CommunicationManagement:
    def __init__(self,e,topic1,topic2):
        self.topic_receive = topic1
        self.topic_send = topic2
        KafkaInitial.topicCreate(self.topic_send,producer_config_path)
        #创建生产者和消费者
        self.producer = KafkaProducer(producer_config_path)
        #uuid1生成一个随机14位序列
        self.consumer = KafkaConsumer(consumer_config_path, str(uuid.uuid1()), self.topic_receive)
        self.event_manager = e
        self.stop_flag = False
        self.message_queue = queue.Queue(0)
        #创建消费者接收信息的线程（收到的消息保存在message_queue中）
        self.receive_exchange_message_thread = Thread(target=receive_message_fcn, args=(self.message_queue, self.consumer, lambda: self.stop_flag,))
        #从消息队列中获取数据并将获取到的保存为event并加入到事件队列中
        self.operator_exchange_message_thread = Thread(target=operate_message_fcn, args=(self.message_queue, self.event_manager, lambda: self.stop_flag,))
        #启动消息接收线程


    #发送消息！！
    def send_exchange_message(self, message):
        self.producer.send(self.topic_send, bytes(message, encoding="utf-8"))
        print('send ' + message + '!')

    def stop(self):
        self.stop_flag = True
        self.event_manager.Stop()
        self.receive_exchange_message_thread.join()
        self.operator_exchange_message_thread.join()

