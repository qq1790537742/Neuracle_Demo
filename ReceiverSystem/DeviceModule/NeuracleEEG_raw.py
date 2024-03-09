import select
import socket
import struct
import threading
import time
import os
from loguru import logger
import numpy as np
from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationInitial import CommunicationInitial
from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationProducer import CommunicationProducer
from EEGPlatformCommunicationModule4py.communicationModuleInterface.CommunicationProducerInterface import \
    CommunicationProducerInterface

confPath = os.path.join(os.path.dirname(os.path.dirname(__file__)), r'Communication', r'config', r'producer-config.json')
print(confPath)
topic = 'NeuracleEEG'


class NeuracleEEGThread(threading.Thread, ):
    def __init__(self, threadName, device, n_chan, hostname, port, srate, t_buffer):
        threading.Thread.__init__(self)
        self.name = threadName
        self.sock = []
        self.device = device
        self.n_chan = n_chan
        self.hostname = hostname
        self.port = port
        self.t_buffer = t_buffer  # 采样时间
        self.srate = srate  # 采样率
        self._update_interval = 0.04  # unit is seconds. eegthread sends TCP/IP socket in 40 milliseconds
        self.producer: CommunicationProducerInterface = CommunicationProducer(confPath)
        self.isSend = True  # 是否发送至Kafka的标志位
        self.logger = logger
        date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.logger.add(fr"Log/NeuracleEEG-{date}.log", rotation="100MB", encoding="utf-8", enqueue=True,
                        compression="zip", retention="1 days")

    def connect(self):
        """
        try to connect data server
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        notconnect = True
        reconnecttime = 0  # 未连接次数
        while notconnect:
            try:
                self.sock.connect((self.hostname, self.port))
                notconnect = False
                self.logger.info('Data server connected')
            except:
                reconnecttime += 1
                self.logger.info('connection failed, retrying for {} times', reconnecttime)
                # print('connection failed, retrying for %d times' % reconnecttime)
                time.sleep(1)
                if reconnecttime > 2:
                    break
        self.shutdown_flag = threading.Event()
        self.shutdown_flag.set()
        self.sock.setblocking(True)
        self.bufsize = int(self.t_buffer * self.n_chan * self.srate * 4)  # set buffer size（通道数*采样点*采样时间*float字节数）
        return notconnect

    def run(self):
        """
        线程开始函数
        """
        self.read_thread()

    def read_thread(self):  # visit eegthread, catch sockets and parse sockets, append parsed data to ringbuffer
        socket_lock = threading.Lock()
        while self.shutdown_flag.isSet():
            if not self.sock:
                break
            rs, _, _ = select.select([self.sock], [], [], 9)
            for r in rs:
                socket_lock.acquire()
                if not self.sock:
                    socket_lock.release()
                    break
                try:
                    raw = r.recv(self.bufsize, socket.MSG_WAITALL)
                except:
                    self.logger.info('can not recieve socket ...')
                    # print('can not recieve socket ...')
                    socket_lock.release()
                    self.sock.close()
                else:
                    data = self.parseData(raw)  # parse data
                    socket_lock.release()
                    data = data.reshape(len(data) // (self.n_chan), self.n_chan)  # 1*k的矩阵转为采样点*通道数
                    data = data.T  # 数组反转
                    # data = self.down_sample(data)  # 降采样至1/4
                    #print(data)
                    data = data.tobytes()  # 转为字节流
                    if data == b'':
                        self.connect()
                    if self.isSend:
                        self.producer.send(topic, data)  # 发送至Kafka

    def parseData(self, raw):
        if 'Neuracle' in self.device:  # parsa data according to Neuracle device protocol
            n = len(raw)  # 二进制流的字节长
            hexData = raw
            n_item = int(len(hexData) / 4 / self.n_chan)  # 一个通道传的4bytes（float）数目
            format_str = '<' + (str(self.n_chan) + 'f') * n_item  # unpack解包
            parse_data = struct.unpack(format_str, hexData)

        else:
            self.logger.info('not avaliable device !')
            # print('not avaliable device !')
            parse_data = []
        return np.asarray(parse_data)

    def down_sample(self, data):
        trigger = data[-1, :]
        #print(trigger)
        # print(trigger)
        trigger_num = len(trigger[trigger != 0])
        if trigger_num == 0:
            down_sample_data = data[:, ::4]  # 降采样至1/4
            return down_sample_data
        print("该数据包中有" + str(trigger_num) + "个trigger")
        down_sample_data = data[:, ::4]  # 降采样至1/4
        print(np.where(trigger != 0))
        trigger_index = np.where(trigger != 0)[0]
        # down_sample_trigger_index = []
        for i in trigger_index:
            down_sample_trigger_index = int(i / 4)
            down_sample_data[-1,down_sample_trigger_index] = trigger[i]
            print(down_sample_data[-1,:])
        return down_sample_data
