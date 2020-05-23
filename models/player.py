class Player:
    def __init__(self, name, name_in_game, op_method, ipt):
        self.name = name
        self.name_in_game = name_in_game
        self.op_method = op_method
        self.terminal = ipt
