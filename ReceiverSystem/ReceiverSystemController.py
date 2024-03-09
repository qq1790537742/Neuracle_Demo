import json
import os
import threading
import time
import uuid
from logging import info
from ReceiverSystem.DeviceModule.NeuracleEEG_raw import NeuracleEEGThread
from loguru import logger

NeuracleEEG_confPath = os.path.join(os.getcwd(),r'..', r'DeviceModule', r'config', r'NeuracleEEG.json')


class ReceiverSystemControl(threading.Thread,):
    def __init__(self):
        threading.Thread.__init__(self)
        self.receiverSystemPrepared = False
        info('采集完成初始化')

    def run(self):
        if not self.receiverSystemPrepared:
            start_ok = self.receiver_test_start()
            while not start_ok:
                start_ok = self.receiver_test_start()
            self.receiverSystemPrepared = True
        self.receiver_start()

    def stop(self):
        self.receiverSystemPrepared = False
        logger.info("采集模块已经停止运行")

    def receiver_test_start(self):
        """
        开启线程并连接至放大器
        @return: 返回是否连接到放大器（bool）
        """
        with open(NeuracleEEG_confPath, 'r') as load_f:
            neuracle = json.load(fp=load_f)
        connecet_kafka = False
        while not connecet_kafka:
            try:
                connecet_kafka = True
            except:
                info('can not connect kafkaserver')
                time.sleep(0.5)
        target_device = neuracle
        self.thread_data_server = NeuracleEEGThread(threadName='NeuracleEEG', device=target_device['device_name'],
                                                    n_chan=target_device['n_chan'],
                                                    hostname=target_device['hostname'], port=target_device['port'],
                                                    srate=target_device['srate'],
                                                    t_buffer=target_device['time_buffer'])  # 建立线程
        self.thread_data_server.logger.info('!!!! The type of device you used is %s' % target_device['device_name'])
        self.thread_data_server.Daemon = True
        notconnect = self.thread_data_server.connect()
        if notconnect:
            self.thread_data_server.logger.debug("Can't connect recorder, Please open the hostport ")
            return False
            # raise TypeError("Can't connect recorder, Please open the hostport ")

        else:
            # thread_data_server.start()
            return True

    def receiver_start(self):
        if not self.thread_data_server.is_alive():
            self.thread_data_server.start()

    def receiver_stop(self):
        self.thread_data_server.isSend = False