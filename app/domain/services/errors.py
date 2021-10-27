class EntityDoesNotExist(Exception):
    """Raised when entity was not found in database."""
    def __init__(self, entity_id):
        self.entity_id = entity_id


class BoxUnavailableException(Exception):
    """
    box不可用
    """
    def __init__(self, entity_id):
        self.entity_id = entity_id


class InvalidOperationException(Exception):
    """
    无效操作
    """


class WrongBoxException(Exception):
    """
    操作了错误的box
    """


class WrongProjectException(Exception):
    """
    项目不对
    """


class NewEntityFailException(Exception):
    """
    新增记录失败
    """