from queue import Queue,Empty
from threading import Thread


class EventManager:
    def __init__(self):
        self.__eventQueue = Queue()  # 存放事件的队列
        self.__active = False   # 事件管理器开关
        self.__thread = Thread(target=self.__Run)  # 事件处理线程
        self.__handlers = {}  # 这里的__handlers是一个字典，用来保存对应的事件的响应函数，其中每个键对应的值是一个列表，列表中保存了对该事件监听的响应函数，一对多

    def __Run(self):
        while self.__active:
            try:
                event = self.__eventQueue.get(block=True, timeout=1)  # 获取事件的阻塞时间设为1秒:如果在1s内队列中有元素，则取出；否则过1s之后报Empty异常
                self.EventProcess(event)   # 运行事件处理函数
            except Empty:
                pass

    def EventProcess(self, event):
        if event.type_ in self.__handlers:  # 检查是否存在对该事件进行监听的处理函数
            for handler in self.__handlers[event.type_]:  # 若存在，则按顺序将事件传递给处理函数执行
                handler(event)  # 这里的handler就是放进去的监听函数，执行EventHandler中类似于 def do_CTOK(self,event)的方法

    def SendEvent(self, event):
        self.__eventQueue.put(event)  # 发送event，向队列中存入event，event对象中包含type和message

    def Start(self):
        self.__active = True  # 将事件管理器设为启动
        self.__thread.start()  # 启动事件处理线程

    def Stop(self):
        self.__active = False  # 将事件管理器设为停止
        self.__thread.join()  # 等待事件处理线程退出

    def AddEventListener(self, type_, handler):
        try:
            handlerList = self.__handlers[type_]  # 尝试获取该事件类型对应的处理函数列表，若无则创建
        except KeyError:
            handlerList = []
            self.__handlers[type_] = handlerList
        if handler not in handlerList:  # 若要注册的处理器不在该事件的处理器列表中，则注册该事件
            handlerList.append(handler)



