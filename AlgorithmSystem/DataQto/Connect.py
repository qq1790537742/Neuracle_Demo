from Common.communication.CommunicaitonManagement import CommunicationManagement
from Common.event.EventManager import EventManager
import socket
from loguru import logger
import sys

sys.path.append('.')

send_topic = "Module2"
receive_topic = "Module1"

class contest:
    def __init__(self):
        self.ip = None
        self.module_id = 1
        self.flag = False
        self.event_manager = EventManager()
        self.conManagement = CommunicationManagement(self.event_manager, receive_topic, send_topic)

    def run(self):
        self.conManagement.receive_exchange_message_thread.start()
        self.conManagement.operator_exchange_message_thread.start()
        self.send_ip()


    def extract_ip(self):
        st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            st.connect(('10.255.255.255', 1))
            IP = st.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            st.close()
        return IP

    def send_ip(self):
        self.ip = self.extract_ip()
        message = 'CTOK'+self.ip + str(self.module_id)
        self.conManagement.send_exchange_message(message)
        self.flag = True


    def send_ctno(self):
        if self.flag:
            self.ip = self.extract_ip()
            message = 'CTNO' + self.ip + str(self.module_id)
            self.conManagement.send_exchange_message(message)
        else:
            logger.debug("请先启动该子模块")












