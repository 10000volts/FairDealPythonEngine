from core.game import GameCard


class EffectObj:
    """
    单个卡片效果的抽象。
    """

    def __init__(self, secret, sec_arg):
        """

        :param secret: 是否为秘密效果(发动对玩家不可见)。
        :param sec_arg: 秘密参数。
        """
        # cost将触发的时点。如：丢弃手牌、选择1张卡为对象
        self.cost_tp_list = list()
        self.secret = secret
        self.sec_arg = sec_arg

    def condition(self):
        """
        是否满足该效果发动的前提条件。
        :return:
        """
        return True

    def cost(self):
        """
        支付cost。
        :return:
        """

    def execute(self):
        """
        执行效果。
        :return:
        """
        pass

    def can_select(self, sender):
        """
        效果/规则选择卡片作为目标时需要筛选出全部可能的选择，
        设置此回调函数以对该效果所属的卡拥有某些不可被选择的情况。
        如：不能成为对方雇员的效果对象、不能被丢弃等等。
        :param sender: 效果的发动者(GameCard类型)。
        :return:
        """
        pass
