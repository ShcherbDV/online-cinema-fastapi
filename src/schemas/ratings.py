from pydantic import BaseModel, Field


class MovieRatingCreateSchema(BaseModel):
    rating: int = Field(..., ge=0, le=10)


class MovieRatingResponseSchema(BaseModel):
    movie_id: int
    rating: int


class MessageResponseSchema(BaseModel):
    message: str
