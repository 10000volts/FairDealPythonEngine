from utils.constants import EGamePhase, EEffectDesc


class Effect:
    """
    单个卡片效果的抽象。
    """

    def __init__(self, desc: EEffectDesc, host,
                 act_phase: EGamePhase=EGamePhase.PLAY_CARD, trigger=False, force=False,
                 secret=False, scr_arg=False, no_src=False, no_reset=False, ef_id=None, can_invalid=True):
        """

        :param desc:
        :param act_phase:
        :param host:
        :param trigger: 是否为触发式效果(触发效果需加入检查队列)。
        :param force:
        :param secret: 是否为秘密效果(发动对玩家不可见)。
        :param scr_arg: 秘密参数。
        :param no_src:
        :param no_reset: 不会被重置，且这类效果也不会被无效(这方面和can_invalid作用相同)。
        :param ef_id: 效果id，用于限制发动。
        :param can_invalid: 是否能被无效
        """
        self.description = desc
        # 该效果能发动的阶段
        self.act_phase = act_phase
        self.game = host.game
        # 宿主(卡片)。
        self.host = host
        # 宿主卡片id。该效果为无源效果时，host为None所以需要用host_id判断。
        self.host_id = host.cid
        self.secret = secret
        self.scr_arg = scr_arg
        # 是否为无源效果(这时，发动的位置与其所属的卡目前所在地无关)。
        self.no_source = no_src
        # 满足条件时是否强制发动。
        self.force = force
        self.trigger = trigger
        self.no_reset = no_reset
        # 已经连锁过的时点。每个效果不能重复连锁单一时点。
        self.reacted = list()
        self.ef_id = ef_id
        self.can_invalid = can_invalid

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        # if len(self.try_tp):
        #     for tp in self.try_tp:
        #         self.game.temp_tp_stack.append(tp)
        #     self.game.enter_time_points()
        #     for tp in self.try_tp:
        #         if not tp.args[-1]:
        #             return False
        return True

    def cost(self, tp):
        """
        支付cost，触发式效果需要在此添加连锁到的时点(且必须在进入新的时点前)。
        :return:
        """
        return True

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        for p in self.game.players:
            sd = self.game.get_player(self.host)
            if (not self.secret) | (p is sd):
                p.update_vc(self.host)
                p.output('act_eff', [None if self.no_source else self.host.vid], p is sd)
