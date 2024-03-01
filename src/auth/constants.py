from enum import Enum


class Permission(str, Enum):
    user = "user"
    customer = "customer"
    admin = "admin"
    superuser = "superuser"
