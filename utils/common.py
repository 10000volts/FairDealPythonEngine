def adj_pos(x, y, sc):
    """
    生成临近的合法坐标。
    :param x:
    :param y:
    :param sc: scale 棋盘规模(边长)。
    :return:
    """
    p = y * sc + x
    r = list()
    if x > 0:
        r.append(p - 1)
    if x < sc - 1:
        r.append(p + 1)
    if y > 0:
        r.append(p - sc)
    if y < sc - 1:
        r.append(p + sc)
    return r
