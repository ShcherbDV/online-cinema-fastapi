from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.dependencies import get_current_user
from database.models import UserModel, MovieCommentModel
from schemas.comments import CommentSchema, CommentCreateSchema, CommentUpdateSchema
from database import get_db

router = APIRouter()

@router.post("/movies/{movie_id}/comments",
             response_model=CommentSchema,
             summary="Write a comment for movie by user",
             description="Add a comment for a movie by user",
             status_code=status.HTTP_201_CREATED,
)
async def create_comment(
        movie_id: int,
        data: CommentCreateSchema,
        db: AsyncSession = Depends(get_db),
        user: UserModel = Depends(get_current_user)
) -> MovieCommentModel:
    """
    Add a new comment to the database.

    This endpoint allows the creation of a new comment to movie by user.

    :param movie_id: The id of movie for adding comment.
    :type movie_id: int
    :param data: The data for adding comment to movie by user.
    :type data: CommentCreateSchema
    :param db: The SQLAlchemy async database session (provided via dependency injection).
    :type db: AsyncSession
    :param user: The SQLAlchemy user model (provided via dependency injection).
    :type user: UserModel

    :return: The created comment.
    :rtype: MovieCommentModel
    """
    comment = MovieCommentModel(
        text=data.text,
        movie_id=movie_id,
        user_id=user.id,
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return comment


@router.get("/movies/{movie_id}/comments",
             response_model=list[CommentSchema],
             summary="Get a paginated list of comments for movie",
             description="<h3>Get a paginated list of comments for movie</h3>",
             status_code=status.HTTP_200_OK,
)
async def get_comments(
        movie_id: int,
        page: int = 1,
        per_page: int = 10,
        db: AsyncSession = Depends(get_db),
):
    """
    Fetch a paginated list of comments from the database (asynchronously).

    This function retrieves a paginated list of comments, allowing the client to specify
    the page number and the number of items per page. It calculates the total pages
    and provides links to the previous and next pages when applicable.

    :param page: The page number to retrieve (1-based index, must be >= 1).
    :type page: int
    :param per_page: The number of items to display per page (must be between 1 and 20).
    :type per_page: int
    :param movie_id: Movie id for getting comments.
    :type movie_id: int
    :param db: The async SQLAlchemy database session (provided via dependency injection).
    :type db: AsyncSession

    :return: A response containing the paginated list of comments and metadata.
    """
    stmt = (select(MovieCommentModel).where(MovieCommentModel.movie_id == movie_id)
            .offset((page - 1) * per_page)
            .limit(per_page))
    result = await db.execute(stmt)

    return result.scalars().all()


@router.patch("/comments/{comment_id}",
             summary="Update existing comment for movie",
             description="<h3>Update existing comment for movie</h3>",
             status_code=status.HTTP_200_OK,
)
async def update_comment(
        comment_id: int,
        data: CommentUpdateSchema,
        db: AsyncSession = Depends(get_db),
        user: UserModel = Depends(get_current_user)
):
    """
    Update a specific comment by its ID.

    This function updates a comment identified by its unique ID.
    If the comment does not exist, a 404 error is raised.
    If comment does not belong user, a 403 error is raised.

    :param comment_id: The unique identifier of the genre to update.
    :type comment_id: int
    :param data: The updated data for the comment.
    :type data: CommentUpdateSchema
    :param db: The SQLAlchemy database session (provided via dependency injection).
    :type db: AsyncSession
    :param user: The SQLAlchemy user model (provided via dependency injection).
    :type user: UserModel

    :raises HTTPException: Raises a 404 error if the comment with the given ID is not found.
    :raises HTTPPException: Raises a 403 error if the comment with the given ID is not belong current user.

    :return: A response indicating the successful update of the comment.
    :rtype: None
    """
    comment = await db.get(MovieCommentModel, comment_id)

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    comment.text = data.text

    await db.commit()

    return {"detail": "Comment updated"}


@router.delete("/comments/{comment_id}",
               summary="Delete existing comment for movie",
               description="<h3>Delete existing comment for movie</h3>",
               status_code=status.HTTP_204_NO_CONTENT
)
async def delete_comment(
        comment_id: int,
        db: AsyncSession = Depends(get_db),
        user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific comment by its ID.

    This function deletes a comment identified by its unique ID.
    If the movie does not exist, a 404 error is raised.
    If comment does not belong user, a 403 error is raised.


    :param comment_id: The unique identifier of the comment to delete.
    :type comment_id: int
    :param db: The SQLAlchemy database session (provided via dependency injection).
    :type db: AsyncSession
    :param user: The SQLAlchemy user model (provided via dependency injection).
    :type user: UserModel

    :raises HTTPException: Raises a 404 error if the comment with the given ID is not found.
    :raises HTTPException: Raises a 403 error if the comment with the given ID is not belong current user.

    :return: A response indicating the successful deletion of the comment.
    :rtype: None
    """
    comment = await db.get(MovieCommentModel, comment_id)

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != user.id and not user.group != "moderator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    await db.delete(comment)
    await db.commit()

    return {"detail": "Comment deleted"}
