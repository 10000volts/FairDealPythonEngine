from utils.enums import enum

CARD_RANK = enum(COMMON=0, GOOD=1, TRUMP=2)

CARD_TYPE = enum(LEADER=0, EMPLOYEE=1, STRATEGY=2)

GAME_PHASE = enum(SP_DECIDE=0, SHOW_CARD=1, EXTRA_DATA=2, PUT_CARD=3, TAKE_CARD=4, MULLIGAN=5, PLAY_CARD=6)

TIME_POINT = enum(
    # 先后手决定阶段末尾 在此时点发动效果的卡：
    #
    SP_DECIDED=10,
    # 公开手牌阶段末尾 在此时点发动效果的卡：
    #
    SHOWED_CARD=20,
    # 附加值生成后 在此时点发动效果的卡：
    # 密灵西、皮亚娜……
    EXTRA_DATA_GENERATING=30,
    # 调查筹码生成后 在此时点发动效果的卡：
    # 数据分析师(如果在生成前就已经是调查筹码则数据分析师的效果将不处理，也不会扣血)
    INVESTIGATOR_GENERATING=40,
    # 单个筹码放置后 在此时点发动效果的卡：
    #
    CARD_PUT=50,
    # 所有筹码放下后，附加值结算时 在此时点发动效果的卡：
    # 婴儿
    EXTRA_DATA_CALC=60,
    # 附加值结算后，=放置阶段结束时 在此时点发动效果的卡：
    # 塔罗 死神
    EXTRA_DATA_CALC_END=70,
    # 对筹码的一次取走操作完成后 在此时点发动效果的卡：
    #
    CARD_TOOK=80,
    # 取走阶段结束时 在此时点发动效果的卡：
    #
    CARD_TAKE_END=90,
    # 调整阶段时 在此时点发动效果的卡：
    # 抢手应届生
    MULLIGAN=100,
    # 调整阶段末尾，=使用阶段开始时 在此时点发动效果的卡：
    # 假博士
    MULLIGAN_END=110,
    # 尝试使雇员入场 在此时点发动效果的卡：
    # 强力姐姐(的副作用效果)
    TRY_SUMMON_EM_CARD=120,
    # 雇员入场时 在此时点发动效果的卡：
    # 陷阱合同
    SUMMON_EM_CARD=121,
    # 雇员入场成功 在此时点发动效果的卡：
    # 流量明星、帮派成员、奇利亚诺、信息大盗 杰拉德……
    SUCC_SUMMON_EM_CARD=122,
    # 雇员入场失败时 在此时点发动效果的卡：
    #
    # FAIL_SUMMON_EM_CARD=123,
    # 尝试发动策略 在此时点发动效果的卡：
    #
    TRY_ACTIVATE_STRATEGY=124,
    # 尝试发动效果 在此时点发动效果的卡：
    # 鲁莽的开发者
    TRY_ACTIVATE_EFFECT=125,
    # 尝试支付代价 在此时点发动效果的卡：
    #
    TRY_PAY_COST=126,
    # 支付代价后，将适用效果时 在此时点发动效果的卡：
    # 识破、智取……
    PAID_COST=127,
    # 效果处理成功后 在此时点发动效果的卡：
    # 网络暴民……
    SUCC_EFFECT_ACTIVATE=128,
    # 效果处理失败后 在此时点发动效果的卡：
    #
    FAIL_EFFECT_ACTIVATE=129,
    # 尝试放置策略 在此时点发动效果的卡：
    # 鲁莽的开发者
    TRY_SET_STRATEGY=130,
    # 放置策略后 在此时点发动效果的卡：
    #
    SET_STRATEGY=131,
    # 尝试放置雇员 在此时点发动效果的卡：
    #
    TRY_SET_EM=132,
    # 放置雇员 在此时点发动效果的卡：
    #
    SET_EM=133,
    # 回合开始时 在此时点发动效果的卡：
    # 工作狂人……
    TURN_BEGIN=134,
    # 抽卡阶段开始时 在此时点发动效果的卡：
    #
    DP_BEGIN=135,
    # 主要阶段1开始时 在此时点发动效果的卡：
    #
    M1_BEGIN=136,
    # 战斗阶段开始时 在此时点发动效果的卡：
    #
    # BP_BEGIN=137,
    # 主要阶段2开始时 在此时点发动效果的卡：
    #
    # M2_BEGIN=138,
    # 回合结束时 在此时点发动效果的卡：
    # 巨额现金流……
    TURN_END=139,
    # 游戏将结束时 在此时点发动效果的卡：
    # 蓝图设计者
    GAME_ENDING=140,
    # 尝试发动攻击 在此时点发动效果的卡：
    #
    TRY_ATTACK=141,
    # 攻击宣言 在此时点发动效果的卡：
    #
    ATTACK_ANNOUNCE=142,
    # 发生攻击时 在此时点发动效果的卡：
    # 诈骗师、甩锅、威吓……
    ATTACKING=143,
    # 攻击伤害判定时 在此时点发动效果的卡：
    # 龙骑士 盖亚coser、偶像新星……
    ATTACK_DAMAGE_JUDGE=144,
    # 攻击后(意味着攻击方在攻击后仍在场上表侧存在) 在此时点发动效果的卡：
    #
    ATTACKED=145,
    # 尝试被摧毁 在此时点发动效果的卡：
    #
    # TRY_DESTROY=146,
    # 被摧毁时 在此时点发动效果的卡：
    # 首席隐私执行官、高级易容、贴身保镖……
    DESTROYING=146,
    # 被摧毁后 在此时点发动效果的卡：
    # 救火队长……
    DESTROYED=147,
    # 离场时 在此时点发动效果的卡：
    # 堆笑推销员……
    OUT_FIELD=148,
    # 离场后 在此时点发动效果的卡：
    #
    OUT_FIELD_END=149,
    # 离开手牌时 在此时点发动效果的卡：
    #
    OUT_HAND=150,
    # 离开手牌后 在此时点发动效果的卡：
    #
    OUT_HAND_END=151,
    # 离开主卡组时 在此时点发动效果的卡：
    #
    OUT_DECK=152,
    # 离开主卡组后 在此时点发动效果的卡：
    #
    OUT_DECK_END=153,
    # 离开副卡组时 在此时点发动效果的卡：
    #
    OUT_SIDE=154,
    # 离开副卡组后 在此时点发动效果的卡：
    #
    OUT_SIDE_END=155,
    # 离开墓地时 在此时点发动效果的卡：
    #
    OUT_GRAVEYARD=156,
    # 离开墓地后 在此时点发动效果的卡：
    #
    OUT_GRAVEYARD_END=157,
    # 离开移除区时 在此时点发动效果的卡：
    #
    OUT_EXILED=158,
    # 离开移除区后 在此时点发动效果的卡：
    # 
    OUT_EXILED_END=159,
    # 入场时 在此时点发动效果的卡：
    #
    IN_FIELD=148,
    # 入场后 在此时点发动效果的卡：
    #
    IN_FIELD_END=149,
    # 加入手牌时 在此时点发动效果的卡：
    #
    IN_HAND=150,
    # 加入手牌后 在此时点发动效果的卡：
    #
    IN_HAND_END=151,
    # 离开主卡组时 在此时点发动效果的卡：
    #
    IN_DECK=152,
    # 离开主卡组后 在此时点发动效果的卡：
    #
    IN_DECK_END=153,
    # 离开副卡组时 在此时点发动效果的卡：
    #
    IN_SIDE=154,
    # 离开副卡组后 在此时点发动效果的卡：
    #
    IN_SIDE_END=155,
    # 离开墓地时 在此时点发动效果的卡：
    #
    IN_GRAVEYARD=156,
    # 离开墓地后 在此时点发动效果的卡：
    #
    IN_GRAVEYARD_END=157,
    # 离开移除区时 在此时点发动效果的卡：
    #
    IN_EXILED=158,
    # 离开移除区后 在此时点发动效果的卡：
    # 
    IN_EXILED_END=159,
    # 尝试丢弃手牌 在此时点发动效果的卡：
    #
    TRY_DISCARD=160,
    # 丢弃手牌时 在此时点发动效果的卡：
    #
    DISCARDING=161,
    # 被丢弃后 在此时点发动效果的卡：
    #
    DISCARDED=162,
    # 尝试奉献 在此时点发动效果的卡：
    #
    TRY_DEVOTRE=163,
    # 奉献时 在此时点发动效果的卡：
    #
    DEVOTING=164,
    # 奉献后 在此时点发动效果的卡：
    #
    DEVOTED=165,
    # 尝试进行契约 在此时点发动效果的卡：
    #
    TRY_CONTRACT=166,
    # 进行契约时 在此时点发动效果的卡：
    #
    TRY_CONTRACTING=167,
    # 进行契约后 在此时点发动效果的卡：
    #
    CONTRACTED=168,
    )
