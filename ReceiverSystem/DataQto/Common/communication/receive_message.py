import time
from ReceiverSystem.DataQto.Common.kafka.exception.exception import TopicNotAvailableException


def receive_message_fcn(message_queue, consumer, stop):
    try:
        # 循环接收消息
        while True:
            # 收信方法调用，当消费者在0.5s时限内能收到的消息时，consumeMsg为bytes()型，本例仅使用str()方法给出简单的反序列化示例，具体反序列化
            # 方法应由使用者决定
            consumeMsg = consumer.receive()
            if consumeMsg:
                message_queue.put(str(consumeMsg)[2:-1])
                print(str(consumeMsg)[2:-1])
            # else:
            #     print("no msg, get: {}".format(type(consumeMsg)))
            time.sleep(0.1)
            if stop():
                print("Exiting receive_exchange_message_fcn!")
                break
    except TopicNotAvailableException as e:
        print(e)