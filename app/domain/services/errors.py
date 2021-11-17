class BoxException(Exception):

    def __init__(self, box_id):
        self.box_id = box_id


class BoxNotExistException(BoxException):
    """Raised when box was not found in database."""


class ProjectNotExistException(BoxException):
    """Raised when project was not found in database."""


class AdminOnlyOperationException(Exception):
    """
    管理员才可操作
    """


class BoxUnavailableException(BoxException):
    """
    box不可用
    """


class VirtualenvNotExistException(BoxException):
    """
    virtualenv环境不存在
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


class UpdatableFieldException(Exception):
    """
    不可update的字段
    """

    def __init__(self, field_name: str):
        self.field_name = field_name
