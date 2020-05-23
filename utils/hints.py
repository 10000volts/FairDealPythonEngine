from utils.constants import EOutOperation

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

    hints={EOutOperation.GAME_START: '对局开始！',
           EOutOperation.ENTER_PHASE: '进入{}阶段！'.format(emphasize_neutral('{}')),
           EOutOperation.END_PHASE: '{}阶段结束！'.format(emphasize_neutral('{}')),
           EOutOperation.END_GAME: '游戏结束！{}获得单局胜利！',
           EOutOperation.END_MATCH: '对局结束！{}以{}:{}获得比赛胜利！',
           EOutOperation.ENTER_TIME_POINT: '时点: {}'.format(emphasize_neutral('{}')),
           EOutOperation.SP_DECIDED: '{}获得了先手！',
           EOutOperation.SHOW_A_CARD: '轮到{}展示1张{}: ',
           EOutOperation.CHOOSE_TARGET: '请您选择{}张：'.format(emphasize_neutral('{}')),
           EOutOperation.ANNOUNCE_TARGET: '选择结果：{}',
           '11': '对局开始！',
           '12': '对局开始！',
           '13': '对局开始！',
           '14': '对局开始！',
           '15': '对局开始！',
           '16': '对局开始！',
           '17': '对局开始！',
           '18': '对局开始！',
           '19': '对局开始！',
           '20': '对局开始！',
           '21': '对局开始！',
           '22': '对局开始！',
           '23': '对局开始！',
           '24': '对局开始！',
           '25': '对局开始！',
           '26': '对局开始！',
           '27': '对局开始！',
           '28': '对局开始！',
           '29': '对局开始！',
           '30': '对局开始！',
           '31': '对局开始！',
           '32': '对局开始！',
           '33': '对局开始！',
           '34': '对局开始！',
           '35': '对局开始！',
           '36': '对局开始！',
           '37': '对局开始！',
           '38': '对局开始！',
           '39': '对局开始！',
           '40': '对局开始！',
           '41': '对局开始！',
           '42': '对局开始！',
           '43': '对局开始！',
           '44': '对局开始！',
           '45': '对局开始！',
           '46': '对局开始！',
           '47': '对局开始！',
           '48': '对局开始！',
           '49': '对局开始！',
           '50': '对局开始！',
           '51': '对局开始！',
           '52': '对局开始！',
           '53': '对局开始！',
           '54': '对局开始！',
           '55': '对局开始！',
           '56': '对局开始！',
           '57': '对局开始！',
           '58': '对局开始！',
           '59': '对局开始！',
           '60': '对局开始！',
           '61': '对局开始！',
           '62': '对局开始！',
           '63': '对局开始！',
           '64': '对局开始！',
           '65': '对局开始！',
           '66': '对局开始！',
           '67': '对局开始！',
           }
