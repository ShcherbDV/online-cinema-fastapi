from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.dependencies import get_current_user
from src.database.models import UserModel, MovieModel
from src.database.models.ratings import MovieRatingModel
from src.schemas.ratings import MovieRatingResponseSchema, MessageResponseSchema, MovieRatingCreateSchema
from database import get_db


router = APIRouter(prefix="/movies", tags=["Movie ratings"])


@router.post("/{movie_id}/rating",
             response_model=MessageResponseSchema,
             summary="Rate a movie by user",
             description="Add or update rate to a movie by user",
             status_code=status.HTTP_200_OK,
)
async def rate_movie(
    movie_id: int,
    data: MovieRatingCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    movie = await db.get(MovieModel, movie_id)

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    stmt = select(MovieRatingModel).where(
        MovieRatingModel.user_id == user.id,
        MovieRatingModel.movie_id == movie_id,
    )
    result = await db.execute(stmt)
    rating_obj = await result.scalar_one_or_none()

    if rating_obj:
        rating_obj.rating = data.rating
    else:
        rating_obj = MovieRatingModel(
            user_id=user.id,
            movie_id=movie_id,
            rating=data.rating,
        )
        db.add(rating_obj)

    await db.commit()
    return MessageResponseSchema(message="Rating saved!")


@router.delete("/{movie_id}/rating",
               response_model=MessageResponseSchema,
               summary="Delete a rate for movie by user",
               description="Delete a rate for movie by user",
               status_code=status.HTTP_204_NO_CONTENT
)
async def remove_rating(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
        user: UserModel = Depends(get_current_user)
):
    stmt = select(MovieRatingModel).where(
        MovieRatingModel.user_id == user.id,
        MovieRatingModel.movie_id == movie_id,
    )
    result = await db.execute(stmt)
    rating_obj = await result.scalar_one_or_none()

    if not rating_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")

    await db.delete(rating_obj)
    await db.commit()

    return MessageResponseSchema(message="Rating deleted!")
