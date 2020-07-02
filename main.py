import sys
import json

from models.player import Player
from utils.hints import Hint

from time import sleep


def main():
    from core.game import Match
    with open(sys.argv[1]) as f:
        j = json.loads(f.read())
    print(j)
    p1j = json.loads(j[2])
    p1 = Player(p1j['info']['op_method'], j[0], p1j['auto_skip'])
    p2j = json.loads(j[3])
    p2 = Player(p2j['info']['op_method'], j[1], p2j['auto_skip'])
    match_config = json.loads(j[4])

    Hint.choose_language('zh-hans')

    main_match = Match(p1, p1j['deck'], p1j['leader_id'],
                       p2, p2j['deck'], p2j['leader_id'],
                       match_config)
    main_match.start()
    # 防止在接收到结果前退出
    sleep(2)


if __name__ == '__main__':
    main()
