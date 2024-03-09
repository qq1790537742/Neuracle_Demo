import time

from AlgorithmSystem.AlgorithmImplement.Interface.AlgorithmInterface import AlgorithmInterface
import math
from scipy import signal
import numpy as np
from AlgorithmSystem.AlgorithmImplement.SSVEP.CCA import CCA


class AlgorithmImplementSSVEP(AlgorithmInterface):
    def __init__(self):
        super().__init__()
        # 定义采样率
        samp_rate = 250
        # 选择导联编号
        # self.select_channel = [51, 52, 53, 54, 55, 56, 57, 58, 59]
        self.select_channel = [1, 2, 3, 4, 5, 6, 7, 8]
        self.select_channel = [i - 1 for i in self.select_channel]
        # trial开始trigger
        self.trial_start_trig = 240
        # trial结束trigger
        self.trial_end_trig = 241
        # 试次开始点
        self.trial_start_point = None
        # 倍频数
        multiple_freq = 5
        # 计算时间
        cal_time = 2
        # 计算偏移时间（s）
        offset_time = 0.14
        # 偏移长度
        self.offset_len = math.floor(offset_time * samp_rate)
        # 计算长度
        self.cal_len = cal_time * samp_rate
        # 频率集合(40个)
        stim_event_freq = [8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8,
                           10.0, 10.2, 10.4, 10.6, 10.8, 11.0, 11.2, 11.4, 11.6, 11.8,
                           12.0, 12.2, 12.4, 12.6, 12.8, 13.0, 13.2, 13.4, 13.6, 13.8,
                           14.0, 14.2, 14.4, 14.6, 14.8, 15.0, 15.2, 15.4, 15.6, 15.8]
        # 预处理滤波器设置
        self.filterB, self.filterA = self.__get_pre_filter(samp_rate)
        # 正余弦参考信号
        target_template_set = []
        # 采样点，产生n到cal_len/samprate之间的等间隔的cal_len个数。
        samp_point = np.linspace(0, (self.cal_len - 1) / samp_rate, int(self.cal_len), endpoint=True)
        # (1 * 计算长度)的二维矩阵
        samp_point = samp_point.reshape(1, len(samp_point))
        # 对于每个频率
        for freq in stim_event_freq:
            # 基频 + 倍频（作为总共的测试频率）
            test_freq = np.linspace(freq, freq * multiple_freq, int(multiple_freq), endpoint=True)
            # (1 * 倍频数量)的二维矩阵
            test_freq = test_freq.reshape(1, len(test_freq))
            # (倍频数量 * 计算长度)的二维矩阵
            num_matrix = 2 * np.pi * np.dot(test_freq.T, samp_point)
            cos_set = np.cos(num_matrix)
            sin_set = np.sin(num_matrix)
            cs_set = np.append(cos_set, sin_set, axis=0)
            target_template_set.append(cs_set)
        # 初始化算法
        self.method = CCA(target_template_set)
        # self.end_flag=False

    def stop(self):
        self.end_flag = True


    def run(self):
        # 是否停止标签
        self.end_flag = False
        # 是否进入计算模式标签
        cal_flag = False
        while not self.end_flag:
            # print(self.end_flag)
            data_model = self.algo_sys_mng.get_data()
            if data_model is None:
                continue
            if not cal_flag:
                # 非计算模式，则进行事件检测
                cal_flag = self.__idle_proc(data_model)
            else:
                # 计算模式，则进行处理
                cal_flag, result = self.__cal_proc(data_model)
                # 如果有结果，则进行报告
                if result is not None:
                    self.algo_sys_mng.report(result)
                    # 清空缓存
                    self.__clear_cache()
            self.end_flag = data_model.finish_flag

    def __idle_proc(self, data_model):
        # 脑电数据+trigger
        data = data_model.data
        # 获取trigger导
        trigger = data[-1, :]
        # trial开始类型的trigger所在位置的索引
        trigger_idx = np.where(trigger == self.trial_start_trig)[0]
        # 脑电数据
        eeg_data = data[0: -1, :]
        if len(trigger_idx) > 0:
            # 有trial开始trigger则进行计算
            cal_flag = True
            trial_start_trig_pos = trigger_idx[0]
            # 从trial开始的位置拼接数据
            self.cache_data = eeg_data[:, trial_start_trig_pos: eeg_data.shape[1]]
        else:
            # 没有trial开始trigger则
            cal_flag = False
            self.trial_start_point = None
            self.__clear_cache()
        return cal_flag

    def __cal_proc(self, data_model):
        # 脑电数据+trigger
        data = data_model.data
        # 获取脑电数据
        eeg_data = data[0: -1, :]
        # 当已缓存的数据大于等于所需要使用的计算数据时，进行计算
        if self.cache_data.shape[1] >= self.cal_len:
            # 获取所需计算长度的数据
            self.cache_data = self.cache_data[:, 0: int(self.cal_len)]
            # 考虑偏移量
            use_data = self.cache_data[:, self.offset_len: self.cache_data.shape[1]]
            # 滤波处理
            use_data = self.__preprocess(use_data)
            # 开始计算，返回计算结果
            result = self.method.recognize(use_data)
            # 停止计算模式
            cal_flag = False
        else:
            # 反之继续采集数据
            self.cache_data = np.append(self.cache_data, eeg_data, axis=1)
            result = None
            cal_flag = True
        return cal_flag, result

    def __get_pre_filter(self, samp_rate):
        fs = samp_rate
        f0 = 50
        Q = 35
        #这两个参数干啥的
        # b, a = signal.iircomb(f0, q, ftype='notch', fs=fs)
        b = np.array([0.95702, 0, 0, 0, 0, -0.95702])
        a = np.array([1, 0, 0, 0, 0, -0.91404])
        return b, a

    def __clear_cache(self):
        self.cache_data = None

    def __preprocess(self, data):
        # 选择使用的导联
        data = data[self.select_channel, :]
        filter_data = signal.filtfilt(self.filterB, self.filterA, data)
        return filter_data
