import logging
from queue import Queue, Empty
from threading import Thread


class Event:
    def __init__(self, event_type=None):
        # 事件类型
        self.event_type = event_type
        # 事件消息
        self.message = None


class EventManager:
    def __init__(self):
        # 无限长事件队列
        self.__event_que = Queue(0)

        # 事件管理flag
        self.__active = False

        # 事件处理线程
        self.__thread = Thread(target=self.__run)
        self.__thread.setDaemon(True)

        # 这里的__handlers是一个字典,用来保存对应的事件的响应函数
        # 其中每一个key对应的value是一个列表,列表中保存了对该事件监听的响应函数,一对多
        self.__handlers = {}

    def __run(self):
        while self.__active:
            try:
                # 获取事件的阻塞时间为1秒:如果在1s内队列中有元素,则取出;否则过1s后报Empty异常
                event = self.__event_que.get(block=True, timeout=1)
                self.__event_process(event)
            except Empty:
                pass

    def __event_process(self, event):
        # 检测是否存在对该事件进行监听的处理函数
        if event.event_type in self.__handlers:
            # 若存在,则按照顺序将事件传递给处理函数执行
            for handler in self.__handlers[event.event_type]:
                handler(event)

    def start(self):
        # 将事件管理flag设置为True
        self.__active = True
        # 启动事件处理线程
        self.__thread.start()

    def stop(self):
        # 将事件管理flag设置为False
        self.__active = False
        # 等待事件处理线程退出
        # self.__thread.join()

    def add_event_listener(self, event_type, handler):
        """
        添加事件监听者
        :param event_type: 事件类型
        :param handler: 针对事件的处理方法
        """
        # 尝试获取该事件类型对应的处理函数列表,若无则创建
        try:
            handler_lst = self.__handlers[event_type]
        except KeyError:
            handler_lst = []
            self.__handlers[event_type] = handler_lst
        # 若要注册的处理器不在该事件的处理器列表中,则注册该事件
        if handler not in handler_lst:
            handler_lst.append(handler)

    def remove_event_listener(self, event_type, handler):
        """
        移除事件监听者
        :param event_type: 事件类型
        :param handler: 针对事件的处理方法
        """
        try:
            handler_lst = self.__handlers[event_type]
            # 如果该函数存在于列表中,则移除
            if handler in handler_lst:
                handler_lst.remove(handler)
            # 如果函数列表为空,则从引擎中移除该事件类型
            if not handler_lst:
                del self.__handlers[event_type]
        except KeyError:
            pass

    def add_event(self, event):
        """
        将事件放入事件队列
        :param event: Event类型事件
        """
        self.__event_que.put(event)
