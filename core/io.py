from utils.hints import hints

import socket
import json
import os
import re

# {'acceptor': socket, ...}
terminal = dict()


class TimeoutException(Exception):
    pass


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


def input_from_socket(p, msg, check_func, special_func, force=True):
    """

    :param p: player
    :param msg: 提示信息
    :param check_func:
    :param special_func: -1时的特殊处理(默认行为为认输)。
    :param force: 是否为强制输入。
    :return:
    """
    while True:
        try:
            output_2_socket(p.upstream, msg)
            ans = terminal[p.upstream].recv(1024).decode()
            # todo: del
            # print('ans ' + ans)
            if re.match('[0-9 ]+$', ans) is None:
                if force:
                    output_2_socket(p.upstream, make_output('in_err', [0]))
                    continue
                else:
                    return None
            # 判断是否为读取信息的指令。
            # info = g.get_info(p, ans)
            # if info is not None:
            #     output_2_socket(p.upstream, make_output('info', info))
            #     continue
            if ' ' in ans:
                ans = [int(x) for x in ans.split(' ')]
                if ans == -1:
                    if special_func(p, ans[1]):
                        return None
                err_code = check_func(*ans)
                if err_code == 0:
                    return ans
                if force:
                    output_2_socket(p.upstream, make_output('in_err', [err_code]))
                    continue
                return None
            else:
                err_code = check_func(int(ans))
                if err_code == 0:
                    return int(ans)
                if force:
                    output_2_socket(p.upstream, make_output('in_err', [err_code]))
                    continue
                return None
        except Exception as ex:
            if type(ex) == TimeoutException:
                raise ex
            if force:
                print(ex)
                output_2_socket(p.upstream, make_output('in_err', [0]))
                continue
            return None


def input_from_local(p, msg, check_func, special_func, force=True):
    pass


def input_from_ai(p, msg, check_func, special_func, force=True):
    return p.upstream.respond(msg)


def output_2_socket(acceptor, msg: str):
    # 处理粘包
    terminal[acceptor].send((msg + '|').encode())


def output_2_local(acceptor, msg: dict):
    print(hints[int(msg['op'])].format(msg['result']))


def output_2_ai(acceptor, msg):
    pass
