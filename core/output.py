import socket
from utils.hints import hints


def send_2_socket(acceptor, msg):
    pass


def send_msg(acceptor, msg: dict):
    print(hints[int(msg['op'])].format(msg['result']))


def send_2_ai(acceptor, msg):
    pass
