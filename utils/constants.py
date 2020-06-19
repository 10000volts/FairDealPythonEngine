from enum import Enum


class ECardRank(Enum):
    COMMON = 0
    GOOD = 1
    TRUMP = 2


class ECardType(Enum):
    LEADER = 1
    EMPLOYEE = 2
    STRATEGY = 3


class EEffectDesc(Enum):
    # 无法描述
    INDESCRIBABLE = 0
    # HP回复
    HEAL = 1
    # 造成伤害
    CAUSE_DAMAGE = 2


class ELocation(Enum):
    ON_FIELD = 1
    HAND = 2
    GRAVE = 4
    EXILED = 8
    DECK = 16
    SIDE = 32
    UNKNOWN = 64
    ANY = 127


class EGamePhase(Enum):
    SP_DECIDE = 0
    INITIALIZE = 1
    SHOW_CARD = 2
    EXTRA_DATA = 3
    PUT_CARD = 4
    TAKE_CARD = 5
    MULLIGAN = 6
    PLAY_CARD = 7


class ETimePoint(Enum):
    """
      时点枚举。
      PH_XXX: 阶段的开始/结束时点。
      TRY_XXX: 尝试……的隐藏时点，只用来判断该效果是否不能发动(因为被封锁)。
      """
    # 游戏开始时 在此时点发动效果的卡：
    # 一些特殊模式下，需要为领袖添加一些隐藏效果。
    PH_GAME_START = 0
    # 先后手决定阶段开始时 在此时点发动效果的卡：
    #
    # PH_SP_DECIDE = 5
    # 先后手决定阶段末尾 在此时点发动效果的卡：
    #
    PH_SP_DECIDE_END = 10
    # 公开手牌阶段开始时 在此时点发动效果的卡：
    #
    PH_SHOWED_CARD = 15
    # 公开手牌阶段末尾 在此时点发动效果的卡：
    #
    PH_SHOWED_CARD_END = 20
    # 额外生成阶段开始时 在此时点发动效果的卡：
    #
    PH_EXTRA_DATA = 25
    # 附加值生成后 在此时点发动效果的卡：
    # 密灵西、皮亚娜……
    EXTRA_DATA_GENERATED = 30
    # 调查筹码生成后 在此时点发动效果的卡：
    # 数据分析师(如果在生成前就已经是调查筹码则数据分析师的效果将不处理，也不会扣血)
    INVESTIGATOR_GENERATED = 40
    # 额外生成阶段末尾 在此时点发动效果的卡：
    #
    PH_EXTRA_DATA_END = 43
    # 放置阶段开始时 在此时点发动效果的卡：
    #
    PH_PUT_CARD = 46
    # 单个筹码放置后 在此时点发动效果的卡：
    #
    CARD_PUT = 50
    # 所有筹码放下后，附加值结算时 在此时点发动效果的卡：
    # 婴儿
    EXTRA_DATA_CALC = 60
    # 附加值结算后，=放置阶段末尾 在此时点发动效果的卡：
    # 塔罗 死神
    PH_PUT_CARD_END = 70
    # 取走阶段开始时 在此时点发动效果的卡：
    #
    PH_TAKE_CARD = 75
    # 对筹码的一次取走操作完成后 在此时点发动效果的卡：
    #
    CARD_TOOK = 80
    # 取走阶段结束时 在此时点发动效果的卡：
    #
    PH_TAKE_CARD_END = 90
    # 调整阶段开始时 在此时点发动效果的卡：
    # 抢手应届生
    PH_MULLIGAN = 100
    # 调整阶段末尾 在此时点发动效果的卡：
    #
    PH_MULLIGAN_END = 110
    # 使用阶段开始时 在此时点发动效果的卡：
    # 假博士
    PH_PLAY_CARD = 115
    # 尝试使雇员入场 在此时点发动效果的卡：
    # 强力姐姐(的副作用效果)
    TRY_SUMMON_EM_CARD = 120
    # 雇员入场时 在此时点发动效果的卡：
    # 陷阱合同
    SUMMON_EM_CARD = 121
    # 雇员入场成功 在此时点发动效果的卡：
    # 流量明星、帮派成员、奇利亚诺、信息大盗 杰拉德……
    SUCC_SUMMON_EM_CARD = 122
    # 雇员入场失败时 在此时点发动效果的卡：
    #
    # FAIL_SUMMON_EM_CARD=123
    # 尝试发动策略 在此时点发动效果的卡：
    #
    # TRY_ACTIVATE_STRATEGY=124
    # 尝试发动效果 在此时点发动效果的卡：
    # 鲁莽的开发者
    TRY_ACTIVATE_EFFECT = 125
    # 尝试支付代价 在此时点发动效果的卡：
    #
    TRY_PAY_COST = 126
    # 支付代价后，将适用效果时 在此时点发动效果的卡：
    # 识破、智取……
    PAID_COST = 127
    # 效果处理成功后 在此时点发动效果的卡：
    # 网络暴民……
    SUCC_EFFECT_ACTIVATE = 128
    # 效果处理失败后 在此时点发动效果的卡：
    #
    FAIL_EFFECT_ACTIVATE = 129
    # 尝试放置策略 在此时点发动效果的卡：
    # 鲁莽的开发者
    TRY_SET_STRATEGY = 130
    # 放置策略后 在此时点发动效果的卡：
    #
    SET_STRATEGY = 131
    # 尝试放置雇员 在此时点发动效果的卡：
    #
    TRY_SET_EM = 132
    # 放置雇员 在此时点发动效果的卡：
    #
    SET_EM = 133
    # 回合开始时 在此时点发动效果的卡：
    # 工作狂人……
    TURN_BEGIN = 134
    # 抽卡阶段开始时 在此时点发动效果的卡：
    #
    DP_BEGIN = 135
    # 主要阶段1开始时 在此时点发动效果的卡：
    #
    M1_BEGIN = 136
    # 战斗阶段开始时 在此时点发动效果的卡：
    #
    # BP_BEGIN=137
    # 主要阶段2开始时 在此时点发动效果的卡：
    #
    # M2_BEGIN=138
    # 回合结束时 在此时点发动效果的卡：
    # 巨额现金流……
    TURN_END = 139
    # 游戏将结束时 在此时点发动效果的卡：
    # 蓝图设计者
    # GAME_ENDING = 140
    # 尝试发动攻击 在此时点发动效果的卡：
    #
    TRY_ATTACK = 141
    # 攻击宣言 在此时点发动效果的卡：
    #
    ATTACK_ANNOUNCE = 142
    # 发生攻击时 在此时点发动效果的卡：
    # 诈骗师、甩锅、威吓……
    ATTACKING = 143
    # 攻击伤害判定时 在此时点发动效果的卡：
    # 龙骑士 盖亚coser、偶像新星……
    ATTACK_DAMAGE_JUDGE = 144
    # 攻击后(意味着攻击方在攻击后仍在场上表侧存在) 在此时点发动效果的卡：
    #
    ATTACKED = 145
    # 尝试被摧毁 在此时点发动效果的卡：
    #
    # TRY_DESTROY=146
    # 被摧毁时 在此时点发动效果的卡：
    # 首席隐私执行官、高级易容、贴身保镖……
    DESTROYING = 146
    # 被摧毁后 在此时点发动效果的卡：
    # 救火队长……
    DESTROYED = 147
    # 离场时 在此时点发动效果的卡：
    # 堆笑推销员……
    OUT_FIELD = 148
    # 离场后 在此时点发动效果的卡：
    #
    OUT_FIELD_END = 149
    # 离开手牌时 在此时点发动效果的卡：
    #
    OUT_HAND = 150
    # 离开手牌后 在此时点发动效果的卡：
    #
    OUT_HAND_END = 151
    # 离开主卡组时 在此时点发动效果的卡：
    #
    OUT_DECK = 152
    # 离开主卡组后 在此时点发动效果的卡：
    #
    OUT_DECK_END = 153
    # 离开副卡组时 在此时点发动效果的卡：
    #
    OUT_SIDE = 154
    # 离开副卡组后 在此时点发动效果的卡：
    #
    OUT_SIDE_END = 155
    # 离开墓地时 在此时点发动效果的卡：
    #
    OUT_GRAVEYARD = 156
    # 离开墓地后 在此时点发动效果的卡：
    #
    OUT_GRAVEYARD_END = 157
    # 离开移除区时 在此时点发动效果的卡：
    #
    OUT_EXILED = 158
    # 离开移除区后 在此时点发动效果的卡：
    #
    OUT_EXILED_END = 159
    # 入场时 在此时点发动效果的卡：
    #
    IN_FIELD = 160
    # 入场后 在此时点发动效果的卡：
    #
    IN_FIELD_END = 161
    # 加入手牌时 在此时点发动效果的卡：
    #
    IN_HAND = 162
    # 加入手牌后 在此时点发动效果的卡：
    #
    IN_HAND_END = 163
    # 加入主卡组时 在此时点发动效果的卡：
    #
    IN_DECK = 164
    # 加入主卡组后 在此时点发动效果的卡：
    #
    IN_DECK_END = 165
    # 加入副卡组时 在此时点发动效果的卡：
    #
    IN_SIDE = 166
    # 加入副卡组后 在此时点发动效果的卡：
    #
    IN_SIDE_END = 167
    # 加入墓地时 在此时点发动效果的卡：
    #
    IN_GRAVEYARD = 168
    # 加入墓地后 在此时点发动效果的卡：
    #
    IN_GRAVEYARD_END = 169
    # 加入移除区时 在此时点发动效果的卡：
    #
    IN_EXILED = 170
    # 加入移除区后 在此时点发动效果的卡：
    #
    IN_EXILED_END = 171
    # 尝试丢弃手牌 在此时点发动效果的卡：
    #
    TRY_DISCARD = 172
    # 丢弃手牌时 在此时点发动效果的卡：
    #
    DISCARDING = 173
    # 被丢弃后 在此时点发动效果的卡：
    #
    DISCARDED = 174
    # 尝试奉献 在此时点发动效果的卡：
    #
    TRY_DEVOTRE = 175
    # 奉献时 在此时点发动效果的卡：
    #
    DEVOTING = 176
    # 奉献后 在此时点发动效果的卡：
    #
    DEVOTED = 177
    # 尝试进行契约 在此时点发动效果的卡：
    #
    TRY_CONTRACT = 178
    # 进行契约时 在此时点发动效果的卡：
    #
    TRY_CONTRACTING = 179
    # 进行契约后 在此时点发动效果的卡：
    #
    CONTRACTED = 180
    # 尝试抽卡 在此时点发动效果的卡：
    #
    TRY_DRAW = 181
    # 抽卡时 在此时点发动效果的卡：
    #
    DRAWING = 182
    # 抽卡后 在此时点发动效果的卡：
    #
    DRAWN = 183
    # 使用阶段将结束时 在此时点发动效果的卡：
    # 蓝图设计者
    PH_PLAY_CARD_ENDING = 184
    # 尝试将效果无效 在此时点发动效果的卡：
    # 各种发动不会被无效的效果
    TRY_EFF_NEGATE = 185
    # 效果将被无效时 在此时点发动效果的卡：
    #
    EFF_NEGATING = 186
    # 效果被无效后 在此时点发动效果的卡：
    #
    EFF_NEGATED = 187
    # 尝试阻挡 在此时点发动效果的卡：
    # 梦想奔流 萨菲尔·逐梦
    TRY_BLOCK = 188
    # 阻挡时 在此时点发动效果的卡：
    #
    BLOCKING = 189
    # 阻挡后 在此时点发动效果的卡：
    #
    BLOCKED = 190
    # 展示卡时 在此时点发动效果的卡：
    #
    SHOWING_CARD = 191
    # 展示卡后 在此时点发动效果的卡：
    # 冠军大力士
    SHOWED_CARD = 192
