from utils.hints import hints
import socket
import json

# {'acceptor': socket, ...}
terminal = dict()


def set_socket(acceptor):
    terminal[acceptor] = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    terminal[acceptor].connect(acceptor)


def input_from_socket(acceptor, msg):
    output_2_socket(acceptor, msg)
    return json.loads(terminal[acceptor].recv(1024).decode())


def input_from_local(acceptor, msg):
    pass


def input_from_ai(acceptor, msg):
    return acceptor.respond(msg)


def output_2_socket(acceptor, msg: str):
    terminal[acceptor].send(msg.encode())


def output_2_local(acceptor, msg: dict):
    print(hints[int(msg['op'])].format(msg['result']))


def output_2_ai(acceptor, msg):
    pass
