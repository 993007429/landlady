class ServerErrorException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

class InvalidCommandException(Exception):
    pass
