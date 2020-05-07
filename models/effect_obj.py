from core.game import GameCard


class EffectObj:
    """
    单个卡片效果的抽象。
    """

    def __init__(self, active_phase, active_location, owner, host, host_id,
                 secret, scr_arg, no_src, force_exec, ttl):
        """

        :param secret: 是否为秘密效果(发动对玩家不可见)。
        :param scr_arg: 秘密参数。
        """
        # 该效果能发动的阶段
        self.active_phase = active_phase
        self.active_location = active_location

        # 持有玩家
        self.owner = owner
        # 宿主(卡片)。
        self.host = host
        # 宿主卡片id。该效果为无源效果时，host为None所以需要用host_id判断。
        self.host_id = host_id
        self.secret = secret
        self.sec_arg = scr_arg
        # 是否为无源效果(如：延时几回合自动发动的效果，这时，发动的位置与其所属的卡目前所在地无关)。
        self.no_source = no_src
        # 满足条件时是否强制发动。
        self.force_exec = force_exec
        # cost及成功适用效果时将触发的时点。如：丢弃手牌、选择1张卡为对象
        self.trigger_tp_list = ttl
        # 效果是否成功发动。
        self.succ_activate = True

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
