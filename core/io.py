from utils.hints import hints
import socket
import json

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
    terminal[acceptor] = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    terminal[acceptor].connect(acceptor)


def input_from_socket(acceptor, msg, check_func):
    while True:
        try:
            output_2_socket(acceptor, msg)
            r = json.loads(terminal[acceptor].recv(1024).decode())
            if check_func(r):
                return r
        except Exception as ex:
            pass
        output_2_socket(acceptor, make_output('in_err'))


def input_from_local(acceptor, msg, func):
    pass


def input_from_ai(acceptor, msg, func):
    return acceptor.respond(msg)


def output_2_socket(acceptor, msg: str):
    terminal[acceptor].send(msg.encode())


def output_2_local(acceptor, msg: dict):
    print(hints[int(msg['op'])].format(msg['result']))


def output_2_ai(acceptor, msg):
    pass
