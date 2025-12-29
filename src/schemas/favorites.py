from pydantic import BaseModel


class FavoriteResponseSchema(BaseModel):
    movie_id: int

    model_config = {
        "from_attributes": True
    }
