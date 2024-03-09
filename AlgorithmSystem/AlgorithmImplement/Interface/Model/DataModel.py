class DataModel:
    def __init__(self):
        # 数据
        self.data = None

        # 当前数据包的起始位置
        self.start_pos = None

        # 是否停止数据接收
        self.finish_flag = False
