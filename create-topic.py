import os
import time
import sys

from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationInitial import CommunicationInitial


if __name__ == '__main__':

    cur_path = os.path.dirname(__file__)
    # 配置文件地址
    # 配置文件中"bootstrap.servers"为必填选项，格式为"[host]:[port]"，请务必在本机系统中将服务器ip映射至host中，
    # 在当前部署方式下，host名称务必为“server”，不要直接使用ip访问！
    # 不清楚kafka服务器地址和端口时请询问kafka服务器维护者
    conf_path = os.path.join(cur_path, r'AlgorithmSystem', r'communication', r"config", 'Initial-config.json')
    # 要创建的topic名
    topic_list = [
        "NeuraScanEEG",
        "Algorithm2Stimulation"
    ]
    # topic创建
    # topic与生产者之间不存在绑定关系，但建议使用者调用生产者向某topic发信前先进行topic创建
    # 该方法接受的第二个参数本为CommunicationInitial类的配置文件地址
    for topic in topic_list:
        topicCreateResult = CommunicationInitial.topicCreate(topic, conf_path)
    print("topic create successfully")
