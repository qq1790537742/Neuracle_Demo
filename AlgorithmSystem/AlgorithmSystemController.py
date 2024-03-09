import sys

from loguru import logger
from multiprocessing import Process
from AlgorithmSystem.AlgorithmImplement.SSVEP.AlgorithmImplementSSVEP import AlgorithmImplementSSVEP
from AlgorithmSystem.Framework.config.SSVEPConfig import SSVEPConfig
from AlgorithmSystem.Framework.AlgorithmSystemManager import AlgorithmSystemManager
from AlgorithmSystem.communication.ReceiveEEGData import ReceiveEEGData
from AlgorithmSystem.communication.CommunicationProducer import KafkaProducer
import threading
class AlgorithmSystemControl:
    def __init__(self):
        self.algo_sys_mng = None
        # 算法系统是否准备完毕flag
        self.algo_sys_prep_flag = False
        # 接收脑电数据的线程
        self.recv_eeg_data_thread = None
        # Kafka的生产者
        self.producer = None
        # 算法实例
        self.algorithm = None
        # 算法配置文件
        self.config = None

    def run_X(self):
        self.Alg_Start = Process(target=self.run)
        self.Alg_Start.start()

    def run(self):
        if not self.algo_sys_prep_flag:
            self.algo_sys_prep()
        self.algo_sys_mng.run()

    def stop_X(self):
        self.Alg_Start.terminate()
        self.Alg_Start.join()
        logger.info("算法模块已经停止运行")


    def stop(self):
        self.algo_sys_prep_flag = False
        self.recv_eeg_data_thread.stop()
        self.algo_sys_mng.stop()
        logger.info("算法模块已经停止运行")
        sys.exit()


    def algo_sys_prep(self):
        # 调用S S V E P的配置文件
        self.config = SSVEPConfig()
        # 创建算法实现实例
        self.algorithm = AlgorithmImplementSSVEP()
        # 创建Kafka生产者
        self.producer = KafkaProducer('Algorithm2Stimulation')
        self.algo_sys_mng = AlgorithmSystemManager()
        self.algo_sys_mng.initial(self.config, self.algorithm, self.producer)
        # 数据通道数
        channel_num = self.config.channel_num
        # 数据采样点数
        sample_num = self.config.sample_num
        # 脑电数据接收线程启动
        eeg_data_topic = "NeuracleEEG"
        self.recv_eeg_data_thread = ReceiveEEGData(eeg_data_topic, self.algo_sys_mng, channel_num, sample_num)
        # 线程的start函数调用run函数？？？？？？？？？
        # 确实是这样的。通过start的方法来启动线程，实现多线程，无需等待run的运行
        self.recv_eeg_data_thread.start()
        logger.info(f'开始从{eeg_data_topic}接收脑电数据')
        # 算法启动
        self.algo_sys_prep_flag = True
