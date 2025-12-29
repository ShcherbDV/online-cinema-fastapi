from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserModel, MovieModel, FavoriteMovieModel
from config.dependencies import get_current_user
from database import get_db


router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post(
    "/{movie_id}",
    summary="Add a movie to a favorite list of user",
    description="<h3>Add a movie to a favorite list of user</h3>",
    status_code=status.HTTP_201_CREATED,
)
async def add_to_favorites(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    movie = await db.get(MovieModel, movie_id)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found"
        )

    stmt = select(FavoriteMovieModel).where(
        FavoriteMovieModel.movie_id == movie_id, FavoriteMovieModel.user_id == user.id
    )

    exists = (await db.execute(stmt)).scalar_one_or_none()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Movie already in favorites"
        )

    favorite = FavoriteMovieModel(
        user_id=user.id,
        movie_id=movie_id,
    )
    db.add(favorite)
    await db.commit()

    return {"detail": "Movie added to favorites"}


@router.delete(
    "/{movie_id}",
    summary="Delete a movie from favorite list of user",
    description="<h3>Delete a movie from favorite list of user</h3>",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_from_favorites(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    stmt = select(FavoriteMovieModel).where(
        FavoriteMovieModel.user_id == user.id,
        FavoriteMovieModel.movie_id == movie_id,
    )
    favorite = (await db.execute(stmt)).scalar_one_or_none()

    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not in favorites")

    await db.delete(favorite)
    await db.commit()
    return {"detail": "Movie deleted from favorites"}
