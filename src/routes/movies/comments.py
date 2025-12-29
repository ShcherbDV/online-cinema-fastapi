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
):
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
        size: int = 10,
        db: AsyncSession = Depends(get_db),
):
    stmt = (select(MovieCommentModel).where(MovieCommentModel.movie_id == movie_id)
            .offset((page - 1) * size)
            .limit(size))
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
    comment = await db.get(MovieCommentModel, comment_id)

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != user.id and not user.group != "moderator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    await db.delete(comment)
    await db.commit()

    return {"detail": "Comment deleted"}
