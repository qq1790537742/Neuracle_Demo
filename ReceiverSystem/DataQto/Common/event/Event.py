class Event:
    """事件对象"""
    def __init__(self, type_=None):
        #print("实例化事件对象：事件类型：{},事件：self.dict".format(type_))
        # 事件类型
        self.type_ = type_
        # 字典用于保存具体的事件数据
        self.message = None

