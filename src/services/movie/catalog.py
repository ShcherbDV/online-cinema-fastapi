from sqlalchemy import select, or_, asc, desc
from sqlalchemy.orm import joinedload

from database.models.favorites import FavoriteMovieModel
from database.models.movies import StarModel, DirectorModel, MovieModel


def build_movie_catalog_query(
    params,
    *,
    only_favorites: bool = False,
    user_id: int | None = None,
):
    stmt = select(MovieModel).options(
        joinedload(MovieModel.genres),
        joinedload(MovieModel.directors),
        joinedload(MovieModel.stars),
    )

    if only_favorites:
        stmt = stmt.join(FavoriteMovieModel).where(
            FavoriteMovieModel.user_id == user_id
        )

    if params.search:
        search = f"%{params.search.lower()}%"
        stmt = stmt.outerjoin(MovieModel.stars).outerjoin(MovieModel.directors)
        stmt = stmt.where(
            or_(
                MovieModel.name.ilike(search),
                MovieModel.description.ilike(search),
                StarModel.name.ilike(search),
                DirectorModel.name.ilike(search),
            )
        )

    if params.year_from:
        stmt = stmt.where(MovieModel.year >= params.year_from)

    if params.year_to:
        stmt = stmt.where(MovieModel.year <= params.year_to)

    if params.imdb_from:
        stmt = stmt.where(MovieModel.imdb >= params.imdb_from)

    if params.imdb_to:
        stmt = stmt.where(MovieModel.imdb <= params.imdb_to)

    if params.sort_by:
        sort_map = {
            "price": MovieModel.price,
            "year": MovieModel.year,
            "imdb": MovieModel.imdb,
            "popularity": MovieModel.votes,
        }

        column = sort_map.get(params.sort_by)
        if column is not None:
            order = asc(column) if params.sort_order == "asc" else desc(column)
            stmt = stmt.order_by(order)

    return stmt
