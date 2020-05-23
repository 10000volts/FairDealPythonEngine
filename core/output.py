import socket
from utils.hints import Hint


def send_2_socket(acceptor, msg):
    pass


def send_msg(acceptor, msg: dict):
    print(Hint.hints[int(msg['op'])].format(msg['result']))


def send_2_ai(acceptor, msg):
    pass
