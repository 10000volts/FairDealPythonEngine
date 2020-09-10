class AI:
    def __init__(self):
        self.msg_queue = list()

    def respond(self, msg, force: bool):
        return

    def restore(self, msg):
        self.msg_queue.append(msg)
