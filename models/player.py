class Player:
    def __init__(self, op_method, us, auto_skip=True):
        self.op_method = op_method
        self.upstream = us

        # 是否自动跳过无法发动效果的时点。
        self.auto_skip = auto_skip
