source venv/bin/activate
python main.py $*
# 参数协议: p1socket文件路径 p2socket文件路径 player1 player2 match_config
# player: {'info': {...}, 'deck': {...}, 'leader_id': ...}
# match_config: {'match_init': 'code...', 
# 'game_config': {...}, 
# 'match_end': 'code...',
# 'match_break': 'code...',
# 'wins_need': int}
# game_config: {'process': [...]}
