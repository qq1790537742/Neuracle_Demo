from AlgorithmSystem.Framework.Model.EventModel import EventModel


class SSVEPConfig:

    def __init__(self):
        # 事件表
        self.event_model_set = []
        for i in range(1, 41):
            self.event_model_set.append(EventModel(i, i, 'TRIALSTART'))
        self.event_model_set.append(EventModel(41, 241, 'TRIALEND'))
        self.event_model_set.append(EventModel(42, 242, 'BLOCKSTART'))
        self.event_model_set.append(EventModel(43, 243, 'BLOCKEND'))
        self.event_model_set.append(EventModel(44, 250, 'RECORDSTART'))
        self.event_model_set.append(EventModel(45, 251, 'RECORDEND'))
        # 算法模块接收数据采样率
        self.freq = 1000
        # 降采样后的数据采样率
        self.down_freq = 250
        # 待识别刺激目标类别总数
        targer_idx = [event_model for event_model in self.event_model_set if event_model.event_type == 'TRIALSTART']
        self.category_num = len(targer_idx)
        # 数据通道数
        self.channel_num = 9
        # 单个数据包的时长（s）
        self.pkg_time = 0.04
        # 单个数据包中的采样点数
        self.sample_num = int(self.freq * self.pkg_time)
