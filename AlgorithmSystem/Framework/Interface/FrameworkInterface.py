from abc import ABCMeta, abstractmethod


class FrameworkInterface(metaclass=ABCMeta):

    @abstractmethod
    def initial(self):
        pass

    @abstractmethod
    def add_task(self, task_name):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def add_data(self, data):
        pass

    @abstractmethod
    def send_report(self, report_model):
        pass
