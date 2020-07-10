from utils.constants import EGamePhase, ELocation, EEffectDesc


class Effect:
    """
    单个卡片效果的抽象。
    """

    def __init__(self, desc: EEffectDesc, act_phase: EGamePhase,
                 owner, host, trigger=False, force_exec=False,
                 secret=False, scr_arg=False, no_src=False, no_reset=False):
        """

        :param desc:
        :param act_phase:
        :param owner:
        :param host:
        :param trigger: 是否为触发式效果(触发效果需加入检查队列)。
        :param force_exec:
        :param secret: 是否为秘密效果(发动对玩家不可见)。
        :param scr_arg: 秘密参数。
        :param no_src:
        :param no_reset: 不会被重置。
        """
        self.description = desc
        # 该效果能发动的阶段
        self.act_phase = act_phase

        # 持有玩家
        self.owner = owner
        self.game = owner.game_now
        # 宿主(卡片)。
        self.host = host
        # 宿主卡片id。该效果为无源效果时，host为None所以需要用host_id判断。
        self.host_id = host.cid
        self.secret = secret
        self.scr_arg = scr_arg
        # 是否为无源效果(这时，发动的位置与其所属的卡目前所在地无关)。
        self.no_source = no_src
        # 满足条件时是否强制发动。
        self.force_exec = force_exec
        self.trigger = trigger
        # 效果是否成功发动。
        self.succ_activate = True
        self.no_reset = no_reset
        # 已经连锁过的时点。每个效果不能重复连锁单一时点。
        self.reacted = list()

    def condition(self):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        return self.game.phase_now == self.act_phase

    def cost(self):
        """
        支付cost，触发式效果需要在此添加连锁到的时点。
        :return:
        """
        return True

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
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
        return True
