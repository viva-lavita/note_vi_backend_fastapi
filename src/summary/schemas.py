from datetime import datetime

from pydantic import UUID4, BaseModel, Field

from src.auth.schemas import ShortUser


class File(BaseModel):
    id: UUID4
    name: str
    path: str
    user: ShortUser

    class Config:
        from_attributes = True


class SummaryImage(BaseModel):
    id: UUID4
    path: str


class Summary(BaseModel):
    id: UUID4
    name: str = Field(max_length=256)
    summary_path: str
    images: list[SummaryImage] | None
    is_public: bool
    created_at: datetime
    updated_at: datetime
    author: ShortUser

    class Config:
        from_attributes = True


class SummaryUpdate(BaseModel):
    name: str | None = Field(max_length=256)
    is_public: bool | None

    # class Config:
    #     from_attributes = True
