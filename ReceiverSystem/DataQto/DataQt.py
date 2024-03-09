import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import Operation


if __name__ == '__main__':
    # 获取UIC窗口操作权限
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    # 调自定义的界面（即刚转换的.py对象）
    Ui = Operation.Ui_MainWindow()
    Ui.setupUi(MainWindow)
    # 显示窗口并释放资源
    MainWindow.show()
    sys.exit(app.exec_())