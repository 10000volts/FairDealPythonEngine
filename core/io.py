from utils.hints import hints

import socket
import json
import os

# {'acceptor': socket, ...}
terminal = dict()


def make_output(op: str, args: list = None, sd=1):
    """

    :param op:
    :param args:
    :param sd: is sender, 是否是操作的主动进行者，以此来实现双方对同一信息的
不同显示。
    :return:
    """
    return json.dumps({'op': op, 'args': args, 'sd': int(sd), 'in': 0})


def make_input(op: str, args: list = None, sd=1):
    """

    :param op:
    :param args:
    :param sd: is sender, 是否是操作的主动进行者，以此来实现双方对同一信息的
不同显示。
    :return:
    """
    return json.dumps({'op': op, 'args': args, 'sd': int(sd), 'in': 1})


def set_socket(acceptor):
    while not os.path.exists(acceptor):
        pass
    terminal[acceptor] = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    terminal[acceptor].connect(acceptor)


def input_from_socket(p, msg, check_func):
    """

    :param p: player
    :param msg: 提示信息
    :param check_func:
    :return:
    """
    while True:
        try:
            output_2_socket(p.upstream, msg)
            ans = terminal[p.upstream].recv(1024).decode()
            # 判断是否为读取信息的指令。
            # info = g.get_info(p, ans)
            # if info is not None:
            #     output_2_socket(p.upstream, make_output('info', info))
            #     continue
            if ' ' in ans:
                ans = [int(x) for x in ans.split(' ')]
                err_code = check_func(*ans)
                if err_code == 0:
                    return ans
                output_2_socket(p.upstream, make_output('in_err', [err_code]))
                continue
            else:
                err_code = check_func(int(ans))
                if err_code == 0:
                    return int(ans)
        except Exception as ex:
            print(ex)
            pass
        output_2_socket(p.upstream, make_output('in_err', [0]))


def input_from_local(p, msg, func):
    pass


def input_from_ai(p, msg, func):
    return p.upstream.respond(msg)


def output_2_socket(acceptor, msg: str):
    # 处理粘包
    terminal[acceptor].send((msg + '|').encode())


def output_2_local(acceptor, msg: dict):
    print(hints[int(msg['op'])].format(msg['result']))


def output_2_ai(acceptor, msg):
    pass
