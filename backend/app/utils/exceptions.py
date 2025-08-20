class NotFoundException(Exception):
    pass

class WrongPasswordException(Exception):
    pass

class RoleNotFoundException(Exception):
    pass

class UserNotFoundException(Exception):
    pass

class PermissionNotFoundException(Exception):
    pass

class PermissionAlreadyAssignedException(Exception):
    pass

class RoleHasNoThisPermissionException(Exception):
    pass

class RoleAlreadyAssignedException(Exception):
    pass

class UserHasNoThisRoleException(Exception):
    pass