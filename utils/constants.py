

class ECardRank:
    COMMON = 0
    GOOD = 1
    TRUMP = 2


class ECardType:
    LEADER = 1
    EMPLOYEE = 2
    STRATEGY = 3


class EEmployeeType:
    COMMON = 1
    CONTRACT = 2
    INHERIT = 4
    PARTNER = 8
    SECRET = 16


class EStrategyType:
    COMMON = 1
    LASTING = 2
    ATTACHMENT = 4
    COUNTER = 8
    CONTRACT = 16
    BACKGROUND = 32


class EEffectDesc:
    # 无法描述
    INDESCRIBABLE = 0
    # 调查筹码
    INVESTIGATE = 1
    # HP回复
    HEAL = 2
    # 造成伤害
    CAUSE_DAMAGE = 3


class ELocation:
    # 先手
    P1 = 1
    # 后手
    P2 = 2
    ON_FIELD = 4
    HAND = 8
    GRAVE = 16
    EXILED = 32
    DECK = 64
    SIDE = 128
    UNKNOWN = 256
    ANY = 511


class EGamePhase:
    # 先后手决定阶段
    SP_DECIDE = 0
    # 初始化阶段
    INITIALIZE = 1
    # 展示阶段
    SHOW_CARD = 2
    # 额外生成阶段
    EXTRA_DATA = 3
    # 放置阶段
    PUT_CARD = 4
    # 取走阶段
    TAKE_CARD = 5
    # 调整阶段
    MULLIGAN = 6
    # 使用阶段
    PLAY_CARD = 7


class ETurnPhase:
    # 回合开始时
    BEGINNING = 0
    # 抽卡阶段
    DP = 1
    # 主要阶段1
    M1 = 2
    # 战斗阶段1
    BP1 = 3
    # 限制战斗阶段1
    LBP1 = 4
    # 限制战斗阶段2
    LBP2 = 5
    # 主要阶段1
    M2 = 6
    # 回合结束时
    ENDING = 7


class EErrorCode:
    # 输入不在范围内。
    OVERSTEP = 1
    # 取走的筹码不合规则(通常情况下，你只能取走单个筹码/两个相邻的筹码)。
    INVALID_TOOK = 2
    # 不能对空筹码进行操作。
    DONT_EXIST = 3
    # 该位置上已存在筹码。
    INVALID_PUT = 4
    # 无法进行这次雇员的入场。
    FORBIDDEN_SUMMON = 5
    # 无法进行这次策略的发动。
    FORBIDDEN_STRATEGY = 6
    # 反制策略必须先在场上盖放1回合才能发动。
    PLAY_COUNTER = 7
    # 使用超过次数限制。
    TIMES_LIMIT = 8
    # 无法识别的卡。
    UNKNOWN_CARD = 9
    # 无法放置非秘密雇员。
    CANNOT_SET = 10
    # 无法进行这次放置。
    FORBIDDEN_SET = 11
    # 无效输入。
    INVALID_INPUT = 12
    # 无法进行这次攻击。
    FORBIDDEN_ATTACK = 13
    # 不能在战斗阶段外攻击/不能在主要阶段外主动使用非触发的效果。
    WRONG_PHASE = 14


class ETimePoint:
    """
      时点枚举。
      PH_XXX: 阶段的开始/结束时点。
      TRY_XXX: 尝试……的隐藏时点，只用来判断该效果是否不能发动(因为被封锁)。 args[-1]: 是否成功。
      XXX_ING: ……时的时点。用来无效/改变效果。
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
    # 多变雇员
    PH_EXTRA_DATA = 25
    # 附加值生成在某张卡时 在此时点发动效果的卡：
    # 愚者、魔术师
    # args: 卡。
    EXTRA_DATA_GENERATING = 27
    # 全部附加值生成后 在此时点发动效果的卡：
    # 皮亚娜……
    EXTRA_DATA_GENERATED = 30
    # 调查筹码生成后 在此时点发动效果的卡：
    # 数据分析师(如果在生成前就已经是调查筹码则数据分析师的效果将不处理，也不会扣血)
    # args: 生成的单个调查筹码。
    INVESTIGATOR_GENERATED = 40
    # 额外生成阶段末尾 在此时点发动效果的卡：
    #
    PH_EXTRA_DATA_END = 43
    # 放置阶段开始时 在此时点发动效果的卡：
    #
    PH_PUT_CARD = 46
    # 单个筹码放置后 在此时点发动效果的卡：
    # args: x, y, 放置的卡
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
    # 强力姐姐(的副作用效果) 不计入常规入场次数的雇员在此时点让可进行次数偷偷+1
    # args[0]: 入场雇员 args[1]: 是否成功
    TRY_SUMMON = 120
    # 雇员入场时 在此时点发动效果的卡：
    # 陷阱合同
    SUMMONING = 121
    # 雇员入场成功 在此时点发动效果的卡：
    # 流量明星、帮派成员、奇利亚诺、信息大盗 杰拉德……
    SUCC_SUMMON = 122
    # 雇员入场失败时 在此时点发动效果的卡：
    #
    # FAIL_SUMMON_EM_CARD=123
    # 尝试发动策略 在此时点发动效果的卡：
    #
    TRY_ACTIVATE_STRATEGY = 124
    # 尝试发动效果(主动/触发) 在此时点发动效果的卡：
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
    # 战斗阶段1开始时 在此时点发动效果的卡：
    #
    BP1_BEGIN=137
    # 主要阶段2开始时 在此时点发动效果的卡：
    #
    M2_BEGIN=138
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
    # 主要用于辅助判断如"从手牌入场时..."的条件
    OUT_FIELD = 148
    # 离场后 在此时点发动效果的卡：
    # 堆笑推销员
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
    # 攻击力计算时 在此时点发动效果的卡：
    # 鼓舞
    # args: 当前攻击力数值。
    ATK_CALCING = 193
    # 攻击力计算后 在此时点发动效果的卡：
    # 飞天拉面神
    # args: 计算后的攻击力数值。
    ATK_CALC = 194
    # 防御力计算时 在此时点发动效果的卡：
    #
    # args: 当前防御力数值。
    DEF_CALCING = 195
    # 防御力计算后 在此时点发动效果的卡：
    #
    # args: 计算后的防御力数值。
    DEF_CALC = 196
    # 限制战斗阶段1开始时 在此时点发动效果的卡：
    #
    LBP1_BEGIN=197
    # 限制战斗阶段2开始时 在此时点发动效果的卡：
    #
    LBP2_BEGIN=198
    # 发动策略时 在此时点发动效果的卡：
    #
    ACTIVATING_STRATEGY = 199
    # 成功发动策略后 在此时点发动效果的卡：
    #
    SUCC_ACTIVATE_STRATEGY = 200
    # 尝试从手牌常规入场结束 在此时点发动效果的卡：
    #
    TRIED_SUMMON = 201
    # 尝试发动策略结束 在此时点发动效果的卡：
    # 不计入策略使用次数的策略在此时点将偷偷加的使用次数扣回
    TRIED_ACTIVATE_STRATEGY = 202
