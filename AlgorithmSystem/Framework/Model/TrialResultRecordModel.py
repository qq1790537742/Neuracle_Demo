class TrialResultRecordModel:

    def __init__(self):
        # 记录中的trialID必须按照读取数据的位置进行记录
        #  不能根据采集数据位置记录
        #  所属试次ID
        self.trial_id = None
        # 所属blockID
        self.block_id = None
        # 试次原始类型
        self.trial_trigger = None
        # 试次开始数据包ID
        self.trial_data_id = None
        # 试次开始位置
        self.trial_start_pos = None
        # 报告结果
        self.result = None
        # 报告时已接收数据位置
        self.report_pos = None
        # 计算时长
        self.report_time = None
