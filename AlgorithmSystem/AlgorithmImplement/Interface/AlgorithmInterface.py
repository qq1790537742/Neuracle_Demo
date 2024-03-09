from abc import ABCMeta, abstractmethod


class AlgorithmInterface(metaclass=ABCMeta):
    def __init__(self):
        self.algo_sys_mng = None

    @abstractmethod
    def run(self):
        pass

    def set_algorithm_system_manager(self, algo_sys_mng):
        self.algo_sys_mng = algo_sys_mng
