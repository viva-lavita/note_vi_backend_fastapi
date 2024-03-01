import json
from uuid import uuid4


class CRUDError(Exception):
    pass


class ObjectNotFoundError(CRUDError):
    pass


class BusinessError(Exception):
    """
    Специфическая ошибка.
    """
    status_code: int
    description: str

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    def to_dict(self) -> dict:
        return dict(
            status_code=self.status_code,
            detail=dict(
                type=self.class_name,
                description=self.description,
            ),
        )

    def __repr__(self) -> str:
        return f"{self.class_name}({self.to_dict()})"

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


def new_uuid() -> str:
    return str(uuid4())


def business_errors_to_swagger(*args) -> dict:
    """"
    Документирует спецификации ошибок в swagger.
    Пример использования:
        @router.get(
            "/{account_id}",
            summary="Get account by id",
            status_code=status.HTTP_200_OK,
            responses=business_errors_to_swagger(AccountNotFoundError),
        )
    """
    responses = dict()

    error_codes = dict()

    errors = []

    for arg in args:
        error_codes[arg.status_code] = []
        errors.append(arg())

    for error in errors:
        error_codes[error.status_code].append(error.to_dict())

    for error in errors:
        examples = error_codes[error.status_code]
        example = examples if len(examples) > 1 else examples[0]
        responses[error.status_code] = dict(
            content={"application/json": {"example": example}}
        )

    return responses