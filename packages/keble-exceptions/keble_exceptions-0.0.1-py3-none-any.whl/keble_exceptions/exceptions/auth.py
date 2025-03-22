from .base import KebleException


class TokenExpired(KebleException):
    def __init__(self):
        super(TokenExpired, self).__init__(status_code=401)


class TokenPurposeUnmatched(KebleException):
    def __init__(self):
        super(TokenPurposeUnmatched, self).__init__(
            status_code=401,
            how_to_resolve={
                "ENGLISH": "You may want to switch your role to user/organization and then switch back to refresh the page.",
                "SIMPLIFIED_CHINESE": "你可以尝试切换角色，从用户切换成组织，然后再切换回来，来重置。这个可能能够解决这个问题。",
            },
        )


class InactiveUser(KebleException):
    def __init__(self):
        super(InactiveUser, self).__init__(status_code=401)


class UserNotFound(KebleException):
    def __init__(self):
        super(UserNotFound, self).__init__(status_code=401)


class UserIdentityVerificationIsRequired(KebleException):
    def __init__(self):
        super(UserIdentityVerificationIsRequired, self).__init__(status_code=428)


class UserOrOrgIdentityNoSufficientToken(KebleException):
    def __init__(self):
        super(UserOrOrgIdentityNoSufficientToken, self).__init__(status_code=402)


class NoObjectPermission(KebleException):
    """No Permission on certain Object"""

    pass


class NoRolePermission(KebleException):
    """No Permission due to Role"""

    pass


class EmailNotRegistered(KebleException):
    pass


class EmailRegistered(KebleException):
    pass


class InvalidEmailConfirmationCode(KebleException):
    pass


class InvalidEmailOrPassword(KebleException):
    pass
