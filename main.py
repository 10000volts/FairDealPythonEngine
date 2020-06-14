import sys
import json

from core.game import Match
from models.player import Player
from time import sleep

main_match: Match = None

if __name__ == '__main__':
    while True:
        sleep(10)
    p1j = json.loads(sys.argv[3])
    p1 = Player(p1j['pid'], p1j['op_method'], sys.argv[1])
    p2j = json.loads(sys.argv[4])
    p2 = Player(p2j['pid'], p2j['op_method'], sys.argv[2])
    match_config = json.loads(sys.argv[5])

    main_match = Match(p1, p1j['deck'], p1j['leader_id'],
                        p2, p2j['deck'], p2j['leader_id'],
                        match_config)
    main_match.start()
