from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class FavoriteMovieModel(Base):
    __tablename__ = "favorite_movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), nullable=False
    )

    movie: Mapped["MovieModel"] = relationship(
        "MovieModel", back_populates="favorited_by"
    )
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="favorite_movies"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_favorite"),
    )
