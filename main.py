import sys
import json

from models.player import Player
from utils.hints import Hint

main_match = None


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

    global main_match
    main_match = Match(p1, p1j['deck'], p1j['leader_id'],
                       p2, p2j['deck'], p2j['leader_id'],
                       match_config)
    main_match.start()


if __name__ == '__main__':
    main()
