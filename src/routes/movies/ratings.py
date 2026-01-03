from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.dependencies import get_current_user
from database.models.accounts import UserModel
from database.models.movies import MovieModel
from database.models.ratings import MovieRatingModel
from schemas.ratings import MessageResponseSchema, MovieRatingCreateSchema
from database import get_db


router = APIRouter()


@router.post(
    "/{movie_id}/rating",
    response_model=MessageResponseSchema,
    summary="Rate a movie by user",
    description="Add or update rate to a movie by user",
    status_code=status.HTTP_200_OK,
)
async def rate_movie(
    movie_id: int,
    data: MovieRatingCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Add a rate to the database to a movie by user.

    This endpoint allows the adding rate to a movie from a user.

    :param movie_id: The ID of the movie to rate for.
    :type movie_id: int
    :param data: The data required to create a rate.
    :type data: MovieRatingCreateSchema
    :param db: The SQLAlchemy async database session (provided via dependency injection).
    :type db: AsyncSession
    :param user: The SQLAlchemy user model (provided via dependency injection).
    :type user: UserModel

    :return: The created a rate for movie by user.
    :rtype: MessageResponseSchema

    :raises HTTPException:
        - 404 if the movie with the given ID is not found.
    """
    movie = await db.get(MovieModel, movie_id)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found"
        )

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


@router.delete(
    "/{movie_id}/rating",
    summary="Delete a rate for movie by user",
    description="Delete a rate for movie by user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_rating(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Delete a rate for a specific movie by its ID.

    This function deletes a rate for movie identified by its unique ID.
    If the rate does not exist, a 404 error is raised.

    :param movie_id: The unique identifier of the rate to delete.
    :type movie_id: int
    :param db: The SQLAlchemy database session (provided via dependency injection).
    :type db: AsyncSession
    :param user: The SQLAlchemy user model (provided via dependency injection).
    :type user: UserModel

    :raises HTTPException: Raises a 404 error if the genre with the given ID is not found.

    :return: A response indicating the successful deletion of the rate.
    :rtype: MessageResponseSchema
    """
    stmt = select(MovieRatingModel).where(
        MovieRatingModel.user_id == user.id,
        MovieRatingModel.movie_id == movie_id,
    )
    result = await db.execute(stmt)
    rating_obj = await result.scalar_one_or_none()

    if not rating_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found"
        )

    await db.delete(rating_obj)
    await db.commit()

    return {"detail": "Rating deleted!"}
