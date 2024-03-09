import numpy as np


class CCA:
    def __init__(self, target_template_set):
        # 正余弦参考信号
        self.target_template_set = target_template_set

    def recognize(self, data):
        p = []
        data = data.T
        # qr分解,data:length*channel
        [Q_temp, R_temp] = np.linalg.qr(data)
        for template in self.target_template_set:
            template = template[:, 0:data.shape[0]]
            template = template.T
            [Q_cs, R_cs] = np.linalg.qr(template)
            data_svd = np.dot(Q_temp.T, Q_cs)
            [U, S, V] = np.linalg.svd(data_svd)
            rho = 1.25 * S[0] + 0.67 * S[1] + 0.5 * S[2]
            p.append(rho)
        result = p.index(max(p))
        result = result+1
        return result
