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


class EChoice:
    # 影响攻击力(对症下药)
    CHANGE_ATK = 0
    # 影响防御力(对症下药)
    CHANGE_DEF = 1
    # 复古左轮(枪械艺术家)
    C50526002 = 2
    # 耍帅左轮(枪械艺术家)
    C79047277 = 3
    # 连发左轮(枪械艺术家)
    C82751803 = 4


class EEffectDesc:
    # 无法描述
    INDESCRIBABLE = 0
    # 调查筹码
    INVESTIGATE = 1
    # HP回复
    HEAL = 2
    # 造成伤害
    DEAL_DAMAGE = 3
    # 伤害增减
    DAMAGE_CHANGE = 4
    # HP减少
    HP_LOST = 5
    # 额外机会
    EXTRA_CHANCE = 10
    # 重置次数
    RESET_TIMES = 11
    # ATK上升
    ATK_GAIN = 30
    # 赋予效果
    REGISTER_EFFECT = 31
    # 变为调查筹码
    BECOME_INVESTIGATE = 32
    # 弱调查筹码
    WEAK_INVESTIGATE = 33
    # 影响力值/附加值变动
    ADDV_CHANGE = 34
    # 摧毁卡。
    DESTROY = 35
    # 特殊入场。
    SPECIAL_SUMMON = 36
    # 移除效果
    REMOVE_EFFECT = 37
    # 无效化
    INVALID = 38
    # ATK变化
    ATK_CHANGE = 39
    # 保护协议
    PROTECT_PROTOCOL = 40
    # 持续时间结束
    EFFECT_END = 41
    # 复原
    RESTORE = 42
    # 禁止/封锁
    FORBIDDEN = 43
    # 常规入场
    SUMMON = 44
    # 穿透
    PIERCE = 45
    # 送去场下
    SEND2GRAVE = 46
    # 加入手牌
    SEND2HAND = 47
    # 移除
    SEND2EXILED = 48
    # 加入卡组
    SEND2DECK = 49
    # 加入副卡组
    SEND2SIDE = 50
    # 丢弃手牌
    DISCARD = 51
    # 改变姿态
    CHANGE_POSTURE = 52
    # 属性变化
    PROPERTY_CHANGE = 53
    # ATK下降
    ATK_LOSE = 54
    # 奉献
    DEVOTE = 55
    # 嘲讽
    TAUNT = 56
    # 被保护
    PROTECT = 57
    # 领袖血量到达上限，抛弃溢出值
    DISCARD_OVERFLOW = 58
    # 支付生命力
    HP_COST = 59
    # 风行
    AGILE = 60
    # 转移目标
    CHANGE_TARGET = 61
    # 穿透汲取
    PIERCE_ABSORB = 62
    # 效果胜利
    VICTORY = 63
    # 盖放卡
    SET_CARD = 64
    # 发动策略
    ACTIVATE_STRATEGY = 65
    # 控制
    CONTROL = 66


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
    # 随机放置阶段
    RANDOM_PUT = 8


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
    # 无法进行这次雇员的入场。(不满足入场条件或被禁止)
    FORBIDDEN_SUMMON = 5
    # 无法进行这次策略的发动。(不满足发动条件或被禁止)
    FORBIDDEN_STRATEGY = 6
    # 反制策略需要满足一定条件才能发动。
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
    # 已经处于明置状态。
    ALREADY_UNCOVERED = 15
    # 这次明置状态的改变被禁止。
    FORBIDDEN_UNCOVER = 16
    # 这次姿态的改变被禁止。
    FORBIDDEN_CP = 17
    # 防御姿态不能攻击。
    DEFEND_POSTURE = 18
    # 没有剩余攻击次数时不能转换姿态。
    NO_TIMES_REMAIN = 19
    # 从副卡组换上的王牌卡数量超过限制。
    NO_MORE_TRUMP = 20
    # 禁止交换。
    FORBIDDEN_EXCHANGE = 21
    # 选择的选项数目不符合要求。
    ILLEGAL_OPTIONS = 22
    # 重复选择同一个选项。
    REPEAT_CHOOSE = 23


class ETimePoint:
    """
      时点枚举。
      PH_XXX: 阶段的开始/结束时点。
      TRY_XXX: 尝试……的隐藏时点，只用来判断该效果是否不能发动(因为被封锁)。 args[-1]: 是否成功。
      TRY_XXX的时点不会修改任何其他的参数。
      XXX_ING: ……时的时点。用来无效/改变效果。 args[-1]: 是否成功。
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
    # args: 卡。 (args[1]: 生成的值)
    EXTRA_DATA_GENERATING = 27
    # 全部附加值生成后 在此时点发动效果的卡：
    # 皮亚娜、密灵西……
    EXTRA_DATA_GENERATED = 30
    # 调查筹码生成后 在此时点发动效果的卡：
    #
    # args: 生成的单个调查筹码。
    INVESTIGATOR_GENERATED = 40
    # 额外生成阶段末尾 在此时点发动效果的卡：
    # 数据分析师
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
    # args[0]: 卡 args[1]: 取走数目
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
    # args[0]: 入场雇员 args[1]: 要降临至其场地的玩家 args[2]: 入场位置
    # args[3]: 入场姿态(非零表示防御姿态) args[4]: 是否成功
    TRY_SUMMON = 120
    # 雇员入场时 在此时点发动效果的卡：
    # 陷阱合同
    # args[0]: 入场雇员 args[1]: 要降临至其场地的玩家 args[2]: 入场位置
    # args[3]: 入场姿态(非零表示防御姿态) args[4]: 是否成功
    SUMMONING = 121
    # 雇员入场成功 在此时点发动效果的卡：
    # 流量明星、帮派成员、奇利亚诺、信息大盗 杰拉德……
    # args[0]: 入场雇员 args[1]: 入场位置 args[2]: 入场姿态(非零表示防御姿态)
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
    # args[0]: 卡
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
    BP1_BEGIN = 137
    # 主要阶段2开始时 在此时点发动效果的卡：
    #
    M2_BEGIN = 138
    # 回合将结束时 在此时点发动效果的卡：
    # 传奇骇客 此时点中放置可选发动的触发效果，不然可能无法达成预期(比如传奇骇客+继承+超人老爹的combo)。
    TURN_ENDING = 140
    # 回合结束后 在此时点发动效果的卡：
    # 巨额现金流…… 此时点中放置必发的触发效果。
    TURN_END = 139
    # 尝试攻击宣言 在此时点发动效果的卡：
    # 不能发动攻击的雇员
    # args[0]: 攻击者
    TRY_ATTACK_ANNOUNCE = 142
    # 尝试发动攻击 在此时点发动效果的卡：
    # 嘲讽的雇员
    # args[0]: 攻击者 args[1]: 攻击目标
    TRY_ATTACK = 141
    # 发生攻击时 在此时点发动效果的卡：
    # 诈骗师、甩锅、威吓……
    # args[0]: 攻击者 args[1]: 攻击目标
    ATTACKING = 143
    # 攻击伤害判定时 在此时点发动效果的卡：
    # 龙骑士 盖亚coser、偶像新星……
    # args[0]: 攻击者 args[1]: 目标 args[2]: 目标所属的玩家应受到的伤害量
    ATTACK_DAMAGE_JUDGE = 144
    # 攻击后 在此时点发动效果的卡：
    # 精神控制
    ATTACKED = 145
    # 尝试被摧毁 在此时点发动效果的卡：
    #
    # TRY_DESTROY=146
    # 被摧毁时 在此时点发动效果的卡：
    # 首席隐私执行官、高级易容、贴身保镖……
    # args[0]: 摧毁者 args[1]: 目标
    DESTROYING = 146
    # 被摧毁后 在此时点发动效果的卡：
    # 救火队长……
    DESTROYED = 147
    # 离场时 在此时点发动效果的卡：
    # 主要用于辅助判断如"从手牌入场时..."的条件
    # args[0]: 卡 args[1]: 区域代码
    OUT_FIELD = 148
    # 离场后 在此时点发动效果的卡：
    # 堆笑推销员
    # args[0]: 卡 args[1]: 区域代码
    OUT_FIELD_END = 149
    # 离开手牌时 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    OUT_HAND = 150
    # 离开手牌后 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    OUT_HAND_END = 151
    # 离开主卡组时 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    OUT_DECK = 152
    # 离开主卡组后 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    OUT_DECK_END = 153
    # 离开副卡组时 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    OUT_SIDE = 154
    # 离开副卡组后 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    OUT_SIDE_END = 155
    # 离开墓地时 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    OUT_GRAVE = 156
    # 离开墓地后 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    OUT_GRAVE_END = 157
    # 离开移除区时 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    OUT_EXILED = 158
    # 离开移除区后 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    OUT_EXILED_END = 159
    # 入场时 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_FIELD = 160
    # 入场后 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_FIELD_END = 161
    # 加入手牌时 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_HAND = 162
    # 加入手牌后 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_HAND_END = 163
    # 加入主卡组时 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_DECK = 164
    # 加入主卡组后 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_DECK_END = 165
    # 加入副卡组时 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_SIDE = 166
    # 加入副卡组后 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_SIDE_END = 167
    # 加入墓地时 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_GRAVE = 168
    # 加入墓地后 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_GRAVE_END = 169
    # 加入移除区时 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_EXILED = 170
    # 加入移除区后 在此时点发动效果的卡：
    #
    # args[0]: 卡 args[1]: 区域代码
    IN_EXILED_END = 171
    # 尝试丢弃手牌 在此时点发动效果的卡：
    #
    # args[0]: 丢弃的卡 args[1]: 是否是选择丢弃
    TRY_DISCARD = 172
    # 丢弃手牌时 在此时点发动效果的卡：
    #
    # args[0]: 丢弃的卡
    DISCARDING = 173
    # 被丢弃后 在此时点发动效果的卡：
    #
    # args[0]: 丢弃的卡
    DISCARDED = 174
    # 尝试奉献 在此时点发动效果的卡：
    #
    # args[0]: 卡
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
    CONTRACTING = 179
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
    # args[0]: 攻击者 args[1]: 阻挡者
    TRY_BLOCK = 188
    # 阻挡时 在此时点发动效果的卡：
    #
    # args[0]: 攻击者 args[1]: 阻挡者
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
    # args[0]: 卡 args[1]: 当前攻击力数值。
    ATK_CALCING = 193
    # 攻击力计算后 在此时点发动效果的卡：
    # 飞天拉面神
    # args[0]: 卡 args[1]: 计算后的攻击力数值。
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
    # args[0]: 策略
    SUCC_ACTIVATE_STRATEGY = 200
    # 尝试从手牌常规入场结束 在此时点发动效果的卡：
    #
    TRIED_SUMMON = 201
    # 尝试发动策略结束 在此时点发动效果的卡：
    # 不计入策略使用次数的策略在此时点将偷偷加的使用次数扣回
    TRIED_ACTIVATE_STRATEGY = 202
    # 重置攻击、阻挡次数时 在此时点发动效果的卡：
    # 枪械艺术家
    RESET_TIMES = 203
    # 造成伤害时 在此时点发动效果的卡：
    # 减弱/增加伤害的卡
    # args[0]: 伤害来源 args[1]: 目标 args[2]: 伤害量，可能是0
    DEALING_DAMAGE = 204
    # 造成伤害后 在此时点发动效果的卡：
    # 事不过三
    # args[0]: 伤害来源 args[1]: 目标 args[2]: 伤害量，可能是0
    DEALT_DAMAGE = 205
    # 尝试支付生命力 在此时点发动效果的卡：
    #
    # args[0]: 支付者 args[1]: 支付量
    TRY_HP_COST = 206
    # 支付生命力时 在此时点发动效果的卡：
    # 减弱/增加伤害的卡
    # args[0]: 支付者 args[1]: 支付量
    HP_COSTING = 207
    # 支付生命力后 在此时点发动效果的卡：
    #
    # args[0]: 支付者 args[1]: 支付量
    HP_COST = 208
    # 尝试为选择效果目标 在此时点发动效果的卡：
    #
    # args[0]: 预想目标
    TRY_CHOOSE_TARGET = 209
    # 选择为效果目标时 在此时点发动效果的卡：
    #
    # args[0]: 预想目标
    CHOOSING_TARGET = 210
    # 选择为效果目标后 在此时点发动效果的卡：
    #
    # args[0]: 预想目标
    CHOSE_TARGET = 211
    # 尝试发动场上盖放的策略 在此时点发动效果的卡：
    #
    # args[0]: 目标
    TRY_UNCOVER_STRATEGY = 212
    # 发动场上盖放的策略时 在此时点发动效果的卡：
    #
    # args[0]: 目标
    UNCOVERING_STRATEGY = 213
    # 发动场上盖放的策略后 在此时点发动效果的卡：
    #
    # args[0]: 目标
    UNCOVERED_STRATEGY = 214
    # 尝试主动明置场上盖放的雇员 在此时点发动效果的卡：
    #
    # args[0]: 目标
    TRY_UNCOVER_EM = 215
    # 主动明置场上盖放的雇员时 在此时点发动效果的卡：
    #
    # args[0]: 目标
    UNCOVERING_EM = 216
    # 主动明置场上盖放的雇员后 在此时点发动效果的卡：
    #
    # args[0]: 目标
    UNCOVERED_EM = 217
    # 尝试改变雇员姿态 在此时点发动效果的卡：
    #
    # args[0]: 目标
    TRY_CHANGE_POSTURE = 218
    # 改变雇员姿态时 在此时点发动效果的卡：
    #
    # args[0]: 目标
    CHANGING_POSTURE = 219
    # 改变雇员姿态后 在此时点发动效果的卡：
    #
    # args[0]: 目标
    CHANGED_POSTURE = 220
    # 询问主动效果 在此时点发动效果的卡：
    # 洛斯(从场下入场)、轮休(从场下移除)……
    # args[0]: 目标
    ASK4EFFECT = 221
    # 尝试回复生命 在此时点发动效果的卡：
    # 终结时刻
    # args[0]: 效果发动者 args[1]: 目标 args[2]: 回复量
    TRY_HEAL = 222
    # 回复生命时 在此时点发动效果的卡：
    #
    # args[0]: 效果发动者 args[1]: 目标 args[2]: 回复量
    HEALING = 223
    # 回复生命后 在此时点发动效果的卡：
    #
    # args[0]: 效果发动者 args[1]: 目标 args[2]: 回复量
    HEALED = 224
    # 风行检查 在此时点发动效果的卡：
    # 风行雇员
    # 在此时点，风行雇员暂时把自己的charge属性设置为True。
    CHARGE_CHECK = 225
    # 原攻击力计算时 在此时点发动效果的卡：
    # 婴儿
    # args[0]: 卡 args[1]: 附加值
    SRC_ATK_CALCING = 226
    # 将对卡产生影响时 在此时点发动效果的卡：
    # 高级智库
    # args[0]: 目标
    INFLUENCING = 227
    # 转发反制 在此时点发动效果的卡：
    # 全部反制策略
    # args[0]: 转发时点
    REDIRECT_COUNTER = 228
    # 确定被摧毁时 在此时点发动效果的卡：
    # 首席隐私执行官、高级易容、贴身保镖……
    # args[0]: 摧毁者 args[1]: 目标
    DESTROYING_SURE = 229
    # 随机放置阶段开始时 在此时点发动效果的卡：
    #
    PH_RANDOM_PUT = 230
    # 随机放置阶段末尾 在此时点发动效果的卡：
    #
    PH_RANDOM_PUT_END = 231
    # 尝试控制权转移 在此时点发动效果的卡：
    # 不会被控制的雇员
    # args[0]: 目标
    TRY_CONTROL = 232
    # 回复生命时 在此时点发动效果的卡：
    #
    # args[0]: 效果发动者 args[1]: 目标 args[2]: 回复量
    # CONTROLLING = 233
    # # 回复生命后 在此时点发动效果的卡：
    # #
    # # args[0]: 效果发动者 args[1]: 目标 args[2]: 回复量
    # CONTROLLED = 234
    # 雇员入场后（无论是否成功） 在此时点发动效果的卡：
    # 蓝图设计者（复原）
    # args[0]: 入场雇员 args[1]: 入场位置 args[2]: 入场姿态(非零表示防御姿态)
    SUMMONED = 235
