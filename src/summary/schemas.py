from datetime import datetime

from pydantic import UUID4, BaseModel, Field

from src.auth.schemas import ShortUser


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


class ShortSummary(BaseModel):
    id: UUID4
    name: str
    summary_path: str
    author: ShortUser

    class Config:
        from_attributes = True


class SummaryUser(BaseModel):
    summary_id: UUID4
    user_id: UUID4
    created_at: datetime
