



from pydantic import UUID4, BaseModel


class FileOut(BaseModel):
    id: UUID4
    name: str
    path: str
    user_id: UUID4

    class Config:
        from_attributes = True
