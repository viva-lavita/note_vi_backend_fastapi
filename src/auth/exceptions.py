class RoleNotFoundError(Exception):
    status_code = 404
    description = "Role is not found"


class TokenNotFoundError(Exception):
    status_code = 404
    description = "Token is not found"
