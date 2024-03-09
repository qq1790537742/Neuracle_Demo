# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Operation.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication,QHBoxLayout,QPushButton,QWidget
from Connect import contest
import time
from loguru import logger
import threading
from AlgorithmSystem.AlgorithmSystemController import AlgorithmSystemControl
import sys

sys.path.append('.')
import json

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 598)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(80, 170, 281, 71))
        self.label.setObjectName("label")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(360, 180, 271, 51))
        self.plainTextEdit.setObjectName("plainTextEdit")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(90, 470, 131, 61))
        self.pushButton.setObjectName("pushButton")
        # 获取文本内容
        self.pushButton.clicked.connect(lambda: self.get_str())
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(600, 470, 131, 61))
        self.pushButton_2.setObjectName("pushButton_2")
        # 退出
        self.pushButton_2.clicked.connect(lambda: self.quit_button())

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(260, 470, 131, 61))
        self.pushButton_3.setObjectName("pushButton_3")
        # 启动模块
        self.pushButton_3.clicked.connect(lambda: self.start_alg())

        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(430, 470, 131, 61))
        self.pushButton_4.setObjectName("pushButton_4")
        # 停止模块
        self.pushButton_4.clicked.connect(lambda: self.stop_module())


        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "算法端"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:20pt;\">请输入总线服务器ip</span></p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "连接"))
        self.pushButton_2.setText(_translate("MainWindow", "退出"))
        self.pushButton_3.setText(_translate("MainWindow", "启动"))
        self.pushButton_4.setText(_translate("MainWindow", "停止"))

    def quit_button(self):
        app = QApplication.instance()
        # 退出应用程序
        app.quit()

    def stop_module(self):
        quit_module = threading.Thread(target=self.quit_module)
        quit_module.start()



    def quit_module(self):
        self.asc.stop_X()
        self.Contest.send_ctno()


    def get_str(self):
        self.str = self.plainTextEdit.toPlainText()
        config_change = threading.Thread(target=self.change_config)
        config_change.start()
        start_connect = threading.Thread(target=self.start_connect)
        start_connect.start()

    def start_alg(self):
        date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        logger.add(sink=fr'./log/stimulation-system-{date}.log', level="INFO", retention='1 week')
        self.asc = AlgorithmSystemControl()
        self.asc.run_X()

    def start_connect(self):
        self.Contest = contest()
        self.AlgEventHandler(self.Contest.event_manager, self.Contest.conManagement)
        self.Contest.run()

    def change_config(self):
        self.writekafka_int_ip(self.kafka_int_ip())
        self.writekafka_consumer_ip(self.kafka_consumer_ip())
        self.writekafka_producer_ip(self.kafka_producer_ip())
        self.writekafka_int_ip_A(self.kafka_int_ip_A())
        self.writekafka_consumer_ip_A(self.kafka_consumer_ip_A())
        self.writekafka_producer_ip(self.kafka_producer_ip_A())

    def change_style(self):
        self.pushButton_3.setStyleSheet("border: 4px solid red; border-radius: 10px;")



    def AlgEventHandler(self, event_mng, conmanager):
        self.exchange_message_management = conmanager
        event_mng.AddEventListener('STOK', self.do_STOK)  # 向事件处理器中添加event和对应的处理函数
        event_mng.Start()

    def do_STOK(self, event):
        msg = event.message
        if msg:
            ip_module = msg['result']
            module_id = int(ip_module[-1])
            if module_id == 1:
                self.change_style()
                logger.info("算法模块成功连接kafka")
            else:
                return 0




    def kafka_int_ip(self):
        with open("./Common/kafka/configuration/Initial-config.json", "rb") as f:
            params = json.load(f)
            ip = self.str
            server = ip + ':' + str(60000)
            print(server)
            params["bootstrap.servers"] = server
        return params

    def writekafka_int_ip(self, params):
        with open("./Common/kafka/configuration/Initial-config.json", "w") as r:
            json.dump(params, r)

    def kafka_consumer_ip(self):
        with open("./Common/kafka/configuration/consumer-config.json", "rb") as f:
            params = json.load(f)
            ip = self.str
            server = ip + ':' + str(60000)
            params["bootstrap.servers"] = server
        return params

    def writekafka_consumer_ip(self, params):
        with open("./Common/kafka/configuration/consumer-config.json", "w") as r:
            json.dump(params, r)

    def kafka_producer_ip(self):
        with open("./Common/kafka/configuration/producer-config.json", "rb") as f:
            params = json.load(f)
            ip = self.str
            server = ip + ':' + str(60000)
            params["bootstrap.servers"] = server
        return params

    def writekafka_producer_ip(self, params):
        with open("./Common/kafka/configuration/producer-config.json", "w") as r:
            json.dump(params, r)




    def kafka_int_ip_A(self):
        with open("../communication/config/Initial-config.json", "rb") as f:
            params = json.load(f)
            ip = self.str
            server = ip + ':' + str(60000)
            print(server)
            params["bootstrap.servers"] = server
        return params

    def writekafka_int_ip_A(self, params):
        with open("../communication/config/Initial-config.json", "w") as r:
            json.dump(params, r)

    def kafka_consumer_ip_A(self):
        with open("../communication/config/consumer-config.json", "rb") as f:
            params = json.load(f)
            ip = self.str
            server = ip + ':' + str(60000)
            params["bootstrap.servers"] = server
        return params

    def writekafka_consumer_ip_A(self, params):
        with open("../communication/config/consumer-config.json", "w") as r:
            json.dump(params, r)

    def kafka_producer_ip_A(self):
        with open("../communication/config/producer-config.json", "rb") as f:
            params = json.load(f)
            ip = self.str
            server = ip + ':' + str(60000)
            params["bootstrap.servers"] = server
        return params

    def writekafka_producer_ip_A(self, params):
        with open("../communication/config/producer-config.json", "w") as r:
            json.dump(params, r)




