from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from schemas.examples.movies import (
    movie_list_response_schema_example,
    movie_item_schema_example,
)


class GenreBaseSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
    }


class GenreListItemSchema(BaseModel):
    id: int
    name: str
    movies_count: int


class GenreListResponseSchema(BaseModel):
    genres: List[GenreListItemSchema]


class GenreCreateSchema(BaseModel):
    name: str

    model_config = {
        "from_attributes": True,
    }


class StarSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
    }


class DirectorSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
    }


class CertificateSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
    }


class MovieBaseSchema(BaseModel):
    name: str = Field(..., max_length=255)
    year: int
    time: int = Field(..., ge=0)
    imdb: float
    votes: int
    meta_score: Optional[float]
    gross: Optional[float]
    description: str
    price: Decimal

    model_config = {
        "from_attributes": True,
    }


class MovieDetailSchema(MovieBaseSchema):
    id: int
    certificate: CertificateSchema
    genres: List[GenreBaseSchema]
    stars: List[StarSchema]
    directors: List[DirectorSchema]

    model_config = {
        "from_attributes": True,
    }


class MovieListItemSchema(BaseModel):
    id: int
    name: str
    year: int
    imdb: float
    description: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"examples": [movie_item_schema_example]},
    }


class MovieListResponseSchema(BaseModel):
    movies: List[MovieListItemSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"examples": [movie_list_response_schema_example]},
    }


class MovieCreateSchema(BaseModel):
    name: str = Field(..., max_length=255)
    year: int
    time: int = Field(..., ge=0)
    imdb: float
    votes: int
    meta_score: Optional[float]
    gross: Optional[float]
    description: str
    price: Decimal
    certificate: str
    genres: List[str]
    stars: List[str]
    directors: List[str]

    model_config = {
        "from_attributes": True,
    }

    @field_validator("genres", "stars", "directors", mode="before")
    @classmethod
    def normalize_list_fields(cls, value: List[str]) -> List[str]:
        return [item.title() for item in value]


class MovieUpdateSchema(BaseModel):
    name: str = Field(..., max_length=255)
    year: int
    time: int = Field(..., ge=0)
    imdb: float
    votes: int
    meta_score: Optional[float]
    gross: Optional[float]
    description: str
    price: Decimal

    model_config = {
        "from_attributes": True,
    }


class MovieCatalogParams(BaseModel):
    search: Optional[str] = Field(
        None, description="Search by title, description, actor, director"
    )
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    imdb_from: Optional[float] = None
    imdb_to: Optional[float] = None

    sort_by: Optional[str] = Field(None, description="price | year | imdb | popularity")
    sort_order: str = Field("desc", description="asc | desc")
