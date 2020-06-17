import sys
import json

from core.game import Match
from models.player import Player
from utils.hints import Hint

main_match: Match = None

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        j = json.loads(f.read())
    print(j)
    p1j = json.loads(j[2])
    p1 = Player(p1j['info']['pid'], p1j['info']['op_method'], j[0])
    p2j = json.loads(j[3])
    p2 = Player(p2j['info']['pid'], p2j['info']['op_method'], j[1])
    match_config = json.loads(j[4])

    Hint.choose_language('zh-hans')

    main_match = Match(p1, p1j['deck'], p1j['leader_id'],
                        p2, p2j['deck'], p2j['leader_id'],
                        match_config)
    main_match.start()
