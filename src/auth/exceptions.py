from src.exceptions import BusinessError


class RoleNotFoundError(BusinessError):
    status_code = 404
    description = "Role is not found"
