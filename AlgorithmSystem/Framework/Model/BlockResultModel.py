class BlockResultModel:
    def __init__(self):
        # 当前blockID，int型
        self.block_id = None

        # 当前block得分，float型
        self.block_score = None

        # 当前block平均用时，float型
        self.block_avg_time = None

    def __str__(self):
        return 'block id：' + str(self.block_id) + '   ' + 'block得分：' + str(self.block_score) + '   ' + 'block平均用时：' + str(self.block_avg_time)
