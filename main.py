import sys
import json

from core.game import Match
from models.player import Player

main_match: Match = None

if __name__ == '__main__':
    p_json = json.loads(sys.argv[1])
    p1 = Player(p_json['name'])
    p_json = json.loads(sys.argv[2])
    p2 = Player(p_json['name'])

    global main_match
    main_match = Match(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
              sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8],
              sys.argv[9])
    if main_match.valid:
        main_match.start()
