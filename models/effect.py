from utils.constants import EGamePhase, EEffectDesc


class DetachList():
    """
    pop变为软删除，成员不能直接访问的列表。
    """
    def __init__(self):
        super().__init__()
        self._index = 0
        self._iter_index = 0
        self._list = list()

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index >= len(self._list):
            raise StopIteration()
        i = self._list[self._iter_index]
        self._iter_index += 1
        return i

    def append(self, e):
        self._list.append(e)

    def pop(self, index: int = -1):
        """
        index只能是-1。
        :param index:
        :return:
        """
        r = self._list[self._index]
        self._index += 1
        return r

    def clear(self):
        self._list.clear()
        self._index = 0


class Effect:
    """
    单个卡片效果的抽象。
    """

    def __init__(self, desc: EEffectDesc, host,
                 act_phase: EGamePhase = EGamePhase.PLAY_CARD, trigger=False, force=False,
                 secret=False, scr_arg=False, no_src=False, no_reset=False, ef_id=None, can_invalid=True,
                 passive=False):
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
        :param passive: 被动效果，不输出。
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
        self.reacted = DetachList()
        self.ef_id = ef_id
        self.can_invalid = can_invalid
        self.react_index = -1
        self.passive = passive
        self.removing = False

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
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
