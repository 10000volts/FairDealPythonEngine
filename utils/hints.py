class Hint:
    @staticmethod
    def emphasize_neutral(text):
        return '<emn|{}>'.format(text)

    @staticmethod
    def emphasize(text):
        """
        强调(我方玩家)。
        :param text:
        :return:
        """
        return '<em|{}>'.format(text)

    @staticmethod
    def emphasize_oppo(text):
        """
        强调(对方玩家)。
        :param text:
        :return:
        """
        return '<emo|{}>'.format(text)

    @staticmethod
    def addi_gte1000(text):
        """
        大于等于1000的附加值
        :param text:
        :return:
        """
        return '<gte10|{}>'.format(text)

    @staticmethod
    def addi_gt0(text):
        return '<gt0|{}>'.format(text)

    @staticmethod
    def addi_e0(text):
        return '<e0|{}>'.format(text)

    @staticmethod
    def addi_lt0(text):
        return '<lt0|{}>'.format(text)

    @staticmethod
    def addi_ltn1000(text):
        return '<ltn10|{}>'.format(text)

    @staticmethod
    def addi_p0(text):
        """
        乘0的附加值
        :param text:
        :return:
        """
        return '<p0|{}>'.format(text)

    @staticmethod
    def addi_pgt1(text):
        """
        乘以大于1的附加值
        :param text:
        :return:
        """
        return '<pgt1|{}>'.format(text)

    @staticmethod
    def addi_lock(text):
        """
        锁定效果
        :param text:
        :return:
        """
        return '<lock|{}>'.format(text)

    @staticmethod
    def addi_blow(text):
        """
        吹回效果
        :param text:
        :return:
        """
        return '<blow|{}>'.format(text)

    @staticmethod
    def lt_source(text):
        """
        小于原本数值。
        :param text:
        :return:
        """
        return '<lts|{}>'.format(text)

    @staticmethod
    def gt_source(text):
        return '<gts|{}>'.format(text)

    @staticmethod
    def card_trump(text):
        return '<ct|{}>'.format(text)

    @staticmethod
    def card_good(text):
        return '<cg|{}>'.format(text)

    @staticmethod
    def card_common(text):
        return '<cc|{}>'.format(text)

    @staticmethod
    def card_token(text):
        """
        我放衍生卡。
        :param text:
        :return:
        """
        return '<ctk|{}>'.format(text)

    @staticmethod
    def card_token_oppo(text):
        return '<ctko|{}>'.format(text)

    @staticmethod
    def choose_language(lan: str = 'zh-hans'):
        from utils import hints_zh_hans
        from utils import hints_en_us
        if lan == 'zh-hans':
            global hints
            hints = hints_zh_hans.hints
        elif lan == 'en-us':
            global hints
            hints = hints_en_us.hints


hints = dict()
