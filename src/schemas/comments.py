from pydantic import BaseModel, Field


class CommentSchema(BaseModel):
    id: int
    text: str
    user_id: int

    model_config = {
        "from_attributes": True,
    }


class CommentCreateSchema(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CommentUpdateSchema(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
