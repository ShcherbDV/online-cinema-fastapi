from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserModel, MovieModel, FavoriteMovieModel
from config.dependencies import get_current_user
from database import get_db

from schemas.movies import (
    MovieListResponseSchema,
    MovieCatalogParams,
    MovieListItemSchema,
)
from services.movie.catalog import build_movie_catalog_query

router = APIRouter()


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
    """
    Add a movie to the favorite list of user.

    This endpoint allows the adding of a movie to favorite list of user.

    :param movie_id: The ID of a movie to add.
    :type movie_id: int
    :param db: The SQLAlchemy async database session (provided via dependency injection).
    :type db: AsyncSession
    :param user: The SQLAlchemy user model (provided via dependency injection).
    :type user: UserModel

    :return: A response indicating the successful adding movie to favorites.
    :rtype: None

    :raises HTTPException:
        - 404 if a movie with the given ID is not found.
        - 409 if input data revoke conflict (like movie is already in the favorite list).
    """
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
    """
    Delete a specific movie by its ID from favorites.

    This function deletes a movie identified by its unique ID from favorites.
    If the movie does not found in favorites, a 404 error is raised.

    :param movie_id: The unique identifier of the movie to delete.
    :type movie_id: int
    :param db: The SQLAlchemy database session (provided via dependency injection).
    :type db: AsyncSession
    :param user: The SQLAlchemy user model (provided via dependency injection).
    :type user: UserModel

    :raises HTTPException: Raises a 404 error if the movie with the given ID is not found.

    :return: A response indicating the successful deletion of the movie.
    :rtype: None
    """
    stmt = select(FavoriteMovieModel).where(
        FavoriteMovieModel.user_id == user.id,
        FavoriteMovieModel.movie_id == movie_id,
    )
    favorite = (await db.execute(stmt)).scalar_one_or_none()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie not in favorites"
        )

    await db.delete(favorite)
    await db.commit()
    return {"detail": "Movie deleted from favorites"}


@router.get(
    "/favorites",
    summary="List of favorites movies user",
    description="List of favorites movies user",
    response_model=MovieListResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_favorites(
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
    params: MovieCatalogParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Fetch a paginated list of movies from the database (asynchronously).

    This function retrieves a paginated list of movies, allowing the client to specify
    the page number and the number of items per page. It calculates the total pages
    and provides links to the previous and next pages when applicable.

    :param page: The page number to retrieve (1-based index, must be >= 1).
    :type page: int
    :param per_page: The number of items to display per page (must be between 1 and 20).
    :type per_page: int
    :param params: Movie catalog query parameters.
    :type params: MovieCatalogParams
    :param db: The async SQLAlchemy database session (provided via dependency injection).
    :type db: AsyncSession
    :param user: The SQLAlchemy user model (provided via dependency injection).
    :type user: UserModel

    :return: A response containing the paginated list of movies and metadata.
    :rtype: MovieListResponseSchema

    :raises HTTPException: Raises a 404 error if no movies are found for the requested page.
    """

    offset = (page - 1) * per_page

    count_stmt = select(func.count(MovieModel.id))
    result_count = await db.execute(count_stmt)
    total_items = result_count.scalar() or 0

    if not total_items:
        raise HTTPException(status_code=404, detail="No movies found.")

    stmt = build_movie_catalog_query(params, only_favorites=True, user_id=user.id)

    stmt = stmt.offset(offset).limit(per_page)

    result_movies = await db.execute(stmt)
    movies = result_movies.scalars().all()

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    movie_list = [MovieListItemSchema.model_validate(movie) for movie in movies]

    total_pages = (total_items + per_page - 1) // per_page

    response = MovieListResponseSchema(
        movies=movie_list,
        prev_page=(
            f"/cinema/favorites/?page={page - 1}&per_page={per_page}"
            if page > 1
            else None
        ),
        next_page=(
            f"/cinema/favorites/?page={page + 1}&per_page={per_page}"
            if page < total_pages
            else None
        ),
        total_pages=total_pages,
        total_items=total_items,
    )
    return response
