import time

from ReceiverSystem.DataQto.Common.event.Event import Event


def operate_message_fcn(message_queue, event_manager, stop):
    while True:
        if message_queue.qsize() > 0:
            message = message_queue.get()
            #长度大于4的时候后有result，小于4的时候没有
            if len(message) > 4:
                #创建新的Event对象
                #将前四个大写字母赋给type_
                event = Event(type_ = message[0:4])
                result = str((message[4:]))
            else:
                event = Event(type_ = message)
                result = 0

            #将result保存到event的message属性中
            event.message = {'result': result}

            #向事件队列中加入事件
            event_manager.SendEvent(event)
        if stop():
            print("Exiting operate_exchange_message_fcn!")
            break
        time.sleep(0.2)