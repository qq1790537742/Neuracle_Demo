import math
import pickle
import queue
import numpy as np
from AlgorithmSystem.AlgorithmImplement.Interface.Model.DataModel import DataModel
from AlgorithmSystem.Framework.Model.BlockResultModel import BlockResultModel
from AlgorithmSystem.Framework.Model.TrialResultRecordModel import TrialResultRecordModel
from loguru import logger


class AlgorithmSystemManager:
    def __init__(self):
        # 算法
        self.algorithm = None
        # 当前block的id
        self.cur_block_id = 0
        # 当前trial的id
        self.cur_trial_id = 0
        # 当前trial的trigger
        self.cur_trial_trigger = None
        # 当前数据的位置
        self.cur_data_pos = 0
        # 当前数据id
        self.cur_data_id = 0
        # 数据队列
        self.data_que = queue.Queue()
        # trial开始trigger
        self.trial_start_trigger = None
        # trial结束trigger
        self.trial_end_trigger = None
        # block开始trigger
        self.block_start_trigger = None
        # block结束trigger
        self.block_end_trigger = None
        # 数据记录开始trigger
        self.record_start_trigger = None
        # 数据记录结束trigger
        self.record_end_trigger = None
        # SSVEP配置文件
        self.config = None
        # 添加数据flag
        self.add_data_flag = False
        # 当前trial结果报告模型
        self.cur_trial_result_record_model = None
        # 实验结束标志位
        self.finish_flag = False
        # 定制接收数据线程的标志位
        self.stop_recv_data_thread_flag = False
        # 当前处理数据的位置
        self.cur_operate_data_pos = 0
        # Kafka生产者
        self.producer = None
        # 缓冲数据
        self.cache_data = None
        # 缓冲数据起始索引
        self.cache_data_idx = 0
        # trial结果模型
        self.trial_result_model = None
        # trial结果模型集合
        self.trial_result_model_set = []
        # block结果模型
        self.block_result_model = None

    def initial(self, config, algorithm, producer):
        self.config = config
        self.trial_start_trigger = [event_model.trigger for event_model in self.config.event_model_set
                                    if event_model.event_type == 'TRIALSTART']
        self.trial_end_trigger = [event_model.trigger for event_model in self.config.event_model_set
                                  if event_model.event_type == 'TRIALEND']
        self.block_start_trigger = [event_model.trigger for event_model in self.config.event_model_set
                                    if event_model.event_type == 'BLOCKSTART']
        self.block_end_trigger = [event_model.trigger for event_model in self.config.event_model_set
                                  if event_model.event_type == 'BLOCKEND']
        self.record_start_trigger = [event_model.trigger for event_model in self.config.event_model_set
                                     if event_model.event_type == 'RECORDSTART']
        self.record_end_trigger = [event_model.trigger for event_model in self.config.event_model_set
                                   if event_model.event_type == 'RECORDEND']
        self.algorithm = algorithm
        self.algorithm.set_algorithm_system_manager(self)
        self.producer = producer

    # 启动算法
    def run(self):
        logger.info('开始运行算法')
        self.algorithm.run()

    def stop(self):
        logger.info('停止算法')
        self.algorithm.stop()

    # 添加数据
    def add_data(self, data):
        # 数据降采样
        down_sample_data = self.down_sample(data)
        # 解包，生成dataModel
        data_model = self.__create_data_model(down_sample_data)
        if data_model is None:
            return
        if data_model.finish_flag is True:
            self.stop_recv_data_thread_flag = True
        # 当前接收数据包ID(连续记录，block变更不清空)
        self.cur_data_id += 1
        # 将接收的dataModel写入队列
        self.data_que.put(data_model)
        # 当前接收数据位置（连续记录）
        self.cur_data_pos = self.cur_data_pos + down_sample_data.shape[1]

    def get_data(self):
        # 判断当前数据队列是否为空
        if self.data_que.empty():
            data_model = None
        else:
            data_model = self.data_que.get()
            # 将刺激目标trigger具体信息抹去变为1
            # 这里的shape是输出列数 设置开始为trigger240，作为标注，最后一行的trigger变为240
            for i in range(data_model.data.shape[1]):
                if data_model.data[-1, i] in self.trial_start_trigger:
                    data_model.data[-1, i] = 240
            # 记录参赛者算法当前获取的数据位置
            self.cur_operate_data_pos = data_model.start_pos + data_model.data.shape[1] - 1
        return data_model

    # 算法报告结果
    def report(self, result):
        logger.info('当前trial的汇报结果为：' + str(result))
        # 如果 当前数据操作位置 >= 当前试次起始位置 并且 当前试次报告结果未报告
        if self.cur_operate_data_pos >= self.trial_result_model.trial_start_pos \
                and self.trial_result_model.result is None:
            # 计算结果
            self.trial_result_model.result = result
            self.trial_result_model.report_pos = self.cur_operate_data_pos
            # 获取当前trial计算所用长度
            data_len = self.cur_operate_data_pos - self.trial_result_model.trial_start_pos
            # 转为时长
            self.trial_result_model.result_report_time = data_len / self.config.down_freq
            # 将当前trial结果报告模型添加至列表中
            self.trial_result_model_set.append(self.trial_result_model)
            # 发送报告,并且将结果转化为二进制。
            msg = b'FDBK' + pickle.dumps(result)
            self.producer.send(msg)

    # 设置停止数据采集Flag
    def set_finish_flag(self):
        # 下一个数据包中finishedFlag为True，发送后重置
        self.finish_flag = True

    def down_sample(self, data):
        # 获取trigger导数据
        trigger = data[-1, :]
        trigger_num = len(trigger[trigger != 0])
        # 如果数据包中没有事件trigger，则直接返回降采样数据
        if trigger_num == 0:
            # 降采样至1/4
            down_sample_data = data[:, ::4]
            return down_sample_data
        # 将降采样至1/4
        down_sample_data = data[:-1, ::4]
        # 获取trigger所在位置的索引
        trigger_idx_arr = np.where(trigger != 0)[0]
        trigger_data = np.zeros((1, down_sample_data.shape[1]))
        for trigger_idx in trigger_idx_arr:
            # 得到trigger
            trigger = trigger[trigger_idx]
            # 降采样后，改trigger应该所在的位置
            down_sample_trigger_idx = int(trigger_idx / 4)
            trigger_data[0][down_sample_trigger_idx] = trigger
        # 将trigger数据拼接到最后一行
        down_sample_data = np.concatenate((down_sample_data, trigger_data), axis=0)
        return down_sample_data

        # 生成dataModel

    def __create_data_model(self, data):
        # 创建DataModel对象实例
        data_model = DataModel()
        # 获取第65行trigger
        trigger_data = data[-1, :]
        # trigger所在位置处的索引数组
        trigger_idx_arr = np.nonzero(trigger_data)[0]
        if len(trigger_idx_arr) > 0:
            for trigger_idx in trigger_idx_arr:
                # 如果是block开始trigger
                if trigger_data[trigger_idx] in self.block_start_trigger:
                    self.block_result_model = None
                    self.cur_block_id += 1
                    # 重置trial id
                    self.cur_trial_id = 0
                # 如果是block结束trigger
                elif trigger_data[trigger_idx] in self.block_end_trigger:
                    # 记录block的得分
                    self.block_result_model = BlockResultModel()
                    self.block_result_model.block_id = self.cur_block_id
                    self.get_score()
                    # 记录得分
                    # print(self.block_result_model)
                    logger.info(f'block id：{str(self.block_result_model.block_id)}，'
                                f'block得分：{str(self.block_result_model.block_score)}，'
                                f'block平均用时：{str(self.block_result_model.block_avg_time)}')
                # 如果是trial开始trigger
                elif trigger_data[trigger_idx] in self.trial_start_trigger:
                    self.cur_trial_id += 1
                    # 获取trial开始位置
                    self.trial_start_pos = self.cur_data_pos + trigger_idx
                    # 获取当前接收数据trial结果trigger
                    self.cur_trial_trigger = trigger_data[trigger_idx]
                    # 创建新trial结果报告模型
                    self.trial_result_model = self.create_trial_result_model(self.trial_start_pos,
                                                                             trigger_data[trigger_idx])
                # 如果是trial结束trigger
                elif trigger_data[trigger_idx] in self.trial_end_trigger:
                    pass
                # 如果是数据记录开始trigger
                elif trigger_data[trigger_idx] in self.record_start_trigger:
                    self.cache_data_idx = trigger_idx
                    self.cache_data = data
                    self.add_data_flag = True
                    # return None
                # 如果是数据记录结束trigger
                elif trigger_data[trigger_idx] in self.record_end_trigger:
                    self.add_data_flag = False
                    self.set_finish_flag()
                    data_model.data = data
                    data_model.start_pos = self.cur_data_pos + 1
                    data_model.finish_flag = self.finish_flag
                    return data_model
        if not self.add_data_flag:
            return None
        # 添加数据65行数据至数据模型
        # temp = np.zeros((data.shape[0], data.shape[1]), dtype=float)
        # temp[0:data.shape[1]-self.cache_data_idx, :] = self.cache_data[self.cache_data_idx:, :]
        # temp[data.shape[1]-self.cache_data_idx:, :] = data[0:self.cache_data_idx, :]
        # data_model.data = temp
        data_model.data = data
        # 当前数据包的起始位置
        data_model.start_pos = self.cur_data_pos + 1
        # 计算完成flag
        data_model.finish_flag = self.finish_flag
        # 将新的数据作为缓存数据
        self.cache_data = data
        return data_model

    # 生成新试次结果报告模型
    def create_trial_result_model(self, trial_start_pos, trial_trigger):
        trial_result_record_model = TrialResultRecordModel()
        # 获取当前trial起始位置
        trial_result_record_model.trial_start_pos = trial_start_pos
        # 获取当前trial标记信息
        trial_result_record_model.trial_trigger = trial_trigger
        # 获取当前blockID
        trial_result_record_model.block_id = self.cur_block_id
        # 获取当前trialID
        trial_result_record_model.trial_id = self.cur_trial_id
        # 获取当前数据包ID
        trial_result_record_model.trial_data_id = self.cur_data_id
        return trial_result_record_model

    # 获取得分
    def get_score(self):
        # 对应于当前block的试次报告结果
        trial_trigger = []
        # 结果
        result = []
        # 计算长度集合
        cal_len_set = []
        # 正确数量
        acc_num = 0
        for trial_result_model in self.trial_result_model_set:
            if trial_result_model.block_id == self.cur_block_id:
                # trial正确trigger列表
                trial_trigger.append(trial_result_model.trial_trigger)
                # 预测结果
                result.append(trial_result_model.result)
                # 算法使用数据长度
                cal_len_set.append(trial_result_model.report_pos - trial_result_model.trial_start_pos)
        # 当前正确答案数
        for i in range(len(trial_trigger)):
            if trial_trigger[i] == result[i]:
                acc_num = acc_num + 1
        # 当前block准确率
        if len(trial_trigger) == 0:
            accuracy = 0
        else:
            accuracy = acc_num / len(trial_trigger)
        # 当前block平均计算长度
        avg_len = np.mean(cal_len_set)
        avg_time = avg_len / self.config.down_freq
        score = 60 * self.calculate_ITR(self.config.category_num, accuracy, avg_time)
        if self.block_result_model is not None:
            self.block_result_model.block_score = score
            self.block_result_model.block_avg_time = avg_time

    def calculate_ITR(self, N, P, T):
        if P == 0:
            ITR = (1 / T) * (math.log(N, 2) + (1 - P) * math.log((1 - P) / (N - 1), 2))
        elif P == 1:
            ITR = (1 / T) * (math.log(N, 2) + P * math.log(P, 2))
        else:
            ITR = (1 / T) * (math.log(N, 2) + (1 - P) * math.log((1 - P) / (N - 1), 2) + P * math.log(P, 2))
        return ITR
