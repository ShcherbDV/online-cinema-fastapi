from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.movies import (
    MovieModel,
    CertificationModel,
    GenreModel,
    StarModel,
    DirectorModel,
)
from database.models.orders import OrderItemModel
from schemas.movies import (
    MovieDetailSchema,
    MovieCreateSchema,
    MovieUpdateSchema,
    GenreBaseSchema,
    GenreCreateSchema,
)
from database import get_db

from config.dependencies import require_moderator

router = APIRouter(dependencies=[Depends(require_moderator)])


@router.post(
    "/movies/",
    response_model=MovieDetailSchema,
    summary="Add a new movie",
    description=(
        "<h3>This endpoint allows clients to add a new movie to the database. "
        "It accepts details such as name, year, genres, stars, directors, and "
        "other attributes. The associated certificate, genres, stars, and directors "
        "will be created or linked automatically.</h3>"
    ),
    responses={
        201: {
            "description": "Movie created successfully.",
        },
        400: {
            "description": "Invalid input.",
            "content": {
                "application/json": {"example": {"detail": "Invalid input data."}}
            },
        },
    },
    status_code=201,
)
async def create_movie(
    movie_data: MovieCreateSchema, db: AsyncSession = Depends(get_db)
) -> MovieDetailSchema:
    """
    Add a new movie to the database.

    This endpoint allows the creation of a new movie with details such as
    name, release date, genres, actors, and languages. It automatically
    handles linking or creating related entities.

    :param movie_data: The data required to create a new movie.
    :type movie_data: MovieCreateSchema
    :param db: The SQLAlchemy async database session (provided via dependency injection).
    :type db: AsyncSession

    :return: The created movie with all details.
    :rtype: MovieDetailSchema

    :raises HTTPException:
        - 409 if a movie with the same name, year and time already exists.
        - 400 if input data is invalid (e.g., violating a constraint).
    """
    existing_stmt = select(MovieModel).where(
        (MovieModel.name == movie_data.name),
        (MovieModel.year == movie_data.year),
        (MovieModel.time == movie_data.time),
    )
    existing_result = await db.execute(existing_stmt)
    existing_movie = existing_result.scalars().first()

    if existing_movie:
        raise HTTPException(
            status_code=409,
            detail=(
                f"A movie with the name '{movie_data.name}', release year"
                f"'{movie_data.year}', adn time '{movie_data.time}' already exists."
            ),
        )

    try:
        certificate_stmt = select(CertificationModel).where(
            CertificationModel.name == movie_data.certificate
        )
        certificate_result = await db.execute(certificate_stmt)
        certificate = certificate_result.scalars().first()
        if not certificate:
            certificate = CertificationModel(name=movie_data.certificate)
            db.add(certificate)
            await db.flush()

        genres = []
        for genre_name in movie_data.genres:
            genre_stmt = select(GenreModel).where(GenreModel.name == genre_name)
            genre_result = await db.execute(genre_stmt)
            genre = genre_result.scalars().first()

            if not genre:
                genre = GenreModel(name=genre_name)
                db.add(genre)
                await db.flush()
            genres.append(genre)

        stars = []
        for star_name in movie_data.stars:
            star_stmt = select(StarModel).where(StarModel.name == star_name)
            star_result = await db.execute(star_stmt)
            star = star_result.scalars().first()

            if not star:
                star = StarModel(name=star_name)
                db.add(star)
                await db.flush()
            stars.append(star)

        directors = []
        for director_name in movie_data.directors:
            director_stmt = select(DirectorModel).where(
                DirectorModel.name == director_name
            )
            director_result = await db.execute(director_stmt)
            director = director_result.scalars().first()

            if not director:
                director = DirectorModel(name=director_name)
                db.add(director)
                await db.flush()
            directors.append(director)

        movie = MovieModel(
            name=movie_data.name,
            year=movie_data.year,
            time=movie_data.time,
            imdb=movie_data.imdb,
            votes=movie_data.votes,
            meta_score=movie_data.meta_score,
            gross=movie_data.gross,
            description=movie_data.description,
            price=movie_data.price,
            certificate=certificate,
            genres=genres,
            stars=stars,
            directors=directors,
        )
        db.add(movie)
        await db.commit()
        await db.refresh(movie, ["genres", "stars", "directors"])

        return MovieDetailSchema.model_validate(movie)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Invalid input data.")


@router.patch(
    "/movies/{movie_id}/",
    summary="Update a movie by ID",
    description=(
        "<h3>Update details of a specific movie by its unique ID.</h3>"
        "<p>This endpoint updates the details of an existing movie. If the movie with "
        "the given ID does not exist, a 404 error is returned.</p>"
    ),
    responses={
        200: {
            "description": "Movie updated successfully.",
            "content": {
                "application/json": {
                    "example": {"detail": "Movie updated successfully."}
                }
            },
        },
        404: {
            "description": "Movie not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Movie with the given ID was not found."}
                }
            },
        },
    },
)
async def update_movie(
    movie_id: int,
    movie_data: MovieUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a specific movie by its ID.

    This function updates a movie identified by its unique ID.
    If the movie does not exist, a 404 error is raised.

    :param movie_id: The unique identifier of the movie to update.
    :type movie_id: int
    :param movie_data: The updated data for the movie.
    :type movie_data: MovieUpdateSchema
    :param db: The SQLAlchemy database session (provided via dependency injection).
    :type db: AsyncSession

    :raises HTTPException: Raises a 404 error if the movie with the given ID is not found.

    :return: A response indicating the successful update of the movie.
    :rtype: None
    """
    stmt = select(MovieModel).where(MovieModel.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(
            status_code=404, detail="Movie with the given ID was not found."
        )

    for field, value in movie_data.model_dump(exclude_unset=True).items():
        setattr(movie, field, value)

    try:
        await db.commit()
        await db.refresh(movie)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Invalid input data.")

    return {"detail": "Movie updated successfully."}


@router.delete(
    "/movies/{movie_id}/",
    summary="Delete a movie by ID",
    description=(
        "<h3>Delete a specific movie from the database by its unique ID.</h3>"
        "<p>If the movie exists, it will be deleted. If it does not exist, "
        "a 404 error will be returned.</p>"
    ),
    responses={
        204: {"description": "Movie deleted successfully."},
        404: {
            "description": "Movie not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Movie with the given ID was not found."}
                }
            },
        },
    },
    status_code=204,
)
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific movie by its ID.

    This function deletes a movie identified by its unique ID.
    If the movie does not exist, a 404 error is raised.

    :param movie_id: The unique identifier of the movie to delete.
    :type movie_id: int
    :param db: The SQLAlchemy database session (provided via dependency injection).
    :type db: AsyncSession

    :raises HTTPException: Raises a 404 error if the movie with the given ID is not found.

    :return: A response indicating the successful deletion of the movie.
    """
    stmt = select(MovieModel).where(MovieModel.id == movie_id)
    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(
            status_code=404, detail="Movie with the given ID was not found."
        )

    purchases_stmt = (
        select(OrderItemModel.id).where(OrderItemModel.movie_id == movie_id).limit(1)
    )
    result = await db.execute(purchases_stmt)
    has_purchases = result.scalar() is not None

    if has_purchases:
        raise HTTPException(
            status_code=409,
            detail="Movie cannot be deleted because it has been purchased by users",
        )

    await db.delete(movie)
    await db.commit()

    return {"detail": "Movie deleted successfully."}


# CRUD functions for genres
@router.post(
    "/genres/",
    response_model=GenreBaseSchema,
    summary="Add a new genre",
    description=(
        "<h3>This endpoint allows moderators to add a new genre to the database.</h3>"
    ),
    responses={
        201: {
            "description": "Genre created successfully.",
        },
        400: {
            "description": "Invalid input.",
            "content": {
                "application/json": {"example": {"detail": "Invalid input data."}}
            },
        },
    },
    status_code=201,
)
async def create_genre(
    genre_data: GenreCreateSchema, db: AsyncSession = Depends(get_db)
) -> MovieDetailSchema:
    """
    Add a new genre to the database.

    This endpoint allows the creation of a new genre.

    :param genre_data: The data required to create a new genre.
    :type genre_data: GenreCreateSchema
    :param db: The SQLAlchemy async database session (provided via dependency injection).
    :type db: AsyncSession

    :return: The created genre.
    :rtype: GenreDetailSchema

    :raises HTTPException:
        - 409 if a genre with the same name already exists.
        - 400 if input data is invalid (e.g., violating a constraint).
    """
    existing_stmt = select(GenreModel).where((GenreModel.name == genre_data.name))
    existing_result = await db.execute(existing_stmt)
    existing_genre = existing_result.scalars().first()

    if existing_genre:
        raise HTTPException(
            status_code=409,
            detail=(f"A genre with the name '{genre_data.name}' already exists."),
        )

    try:
        genre = GenreModel(name=genre_data.name)
        db.add(genre)
        await db.commit()
        await db.refresh(genre)

        return GenreBaseSchema.model_validate(genre)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Invalid input data.")


@router.patch(
    "/genres/{genre_id}/",
    summary="Update a genre by ID",
    description=(
        "<h3>Update name of a specific genre by its unique ID.</h3>"
        "<p>This endpoint updates the name of an existing genre. If the genre with "
        "the given ID does not exist, a 404 error is returned.</p>"
    ),
    responses={
        200: {
            "description": "Genre updated successfully.",
            "content": {
                "application/json": {
                    "example": {"detail": "Movie updated successfully."}
                }
            },
        },
        404: {
            "description": "Genre not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Genre with the given ID was not found."}
                }
            },
        },
    },
)
async def update_genre(
    genre_id: int,
    genre_data: MovieCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a specific genre by its ID.

    This function updates a genre identified by its unique ID.
    If the genre does not exist, a 404 error is raised.

    :param genre_id: The unique identifier of the genre to update.
    :type genre_id: int
    :param genre_data: The updated data for the genre.
    :type genre_data: GenreCreateSchema
    :param db: The SQLAlchemy database session (provided via dependency injection).
    :type db: AsyncSession

    :raises HTTPException: Raises a 404 error if the genre with the given ID is not found.

    :return: A response indicating the successful update of the genre.
    :rtype: None
    """
    stmt = select(GenreModel).where(GenreModel.id == genre_id)
    result = await db.execute(stmt)
    genre = result.scalars().first()

    if not genre:
        raise HTTPException(
            status_code=404, detail="Genre with the given ID was not found."
        )

    for field, value in genre_data.model_dump(exclude_unset=True).items():
        setattr(genre, field, value)

    try:
        await db.commit()
        await db.refresh(genre)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Invalid input data.")

    return {"detail": "Genre updated successfully."}


@router.delete(
    "/genres/{genre_id}/",
    summary="Delete a genre by ID",
    description=(
        "<h3>Delete a specific genre from the database by its unique ID.</h3>"
        "<p>If the genre exists, it will be deleted. If it does not exist, "
        "a 404 error will be returned.</p>"
    ),
    responses={
        204: {"description": "Genre deleted successfully."},
        404: {
            "description": "Genre not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Genre with the given ID was not found."}
                }
            },
        },
    },
    status_code=204,
)
async def delete_genre(
    genre_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific movie by its ID.

    This function deletes a movie identified by its unique ID.
    If the movie does not exist, a 404 error is raised.

    :param genre_id: The unique identifier of the genre to delete.
    :type genre_id: int
    :param db: The SQLAlchemy database session (provided via dependency injection).
    :type db: AsyncSession

    :raises HTTPException: Raises a 404 error if the genre with the given ID is not found.

    :return: A response indicating the successful deletion of the genre.
    :rtype: None
    """
    stmt = select(GenreModel).where(GenreModel.id == genre_id)
    result = await db.execute(stmt)
    genre = result.scalars().first()

    if not genre:
        raise HTTPException(
            status_code=404, detail="Genre with the given ID was not found."
        )

    await db.delete(genre)
    await db.commit()

    return {"detail": "Genre deleted successfully."}
