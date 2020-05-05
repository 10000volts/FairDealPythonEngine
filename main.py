import sys
from core.game import Match

if __name__ == '__main__':
    m = Match(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
              sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8],
              sys.argv[9])
    if m.valid:
        m.start()