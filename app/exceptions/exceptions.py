class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


class UserNotFoundRefreshTokenError(Exception):
    pass


class UserDutiesNotFoundError(Exception):
    pass


class ExcelParsingError(Exception):
    pass


class VigilsTypeNotFound(Exception):
    pass


class NoVigilsDataFromExcel(Exception):
    pass


class ResponsibleTypeError(Exception):
    pass

class ErrorTaskSettings(Exception):
    pass

class TaskNotFound(Exception):
    pass