from fastapi import FastAPI

from routes import accounts
from routes.movies import catalog, moderator, comments, favorites, ratings

app = FastAPI(
    title="Online Cinema API",
    description="A simple API for management movies and users in online cinema",
)

api_version_prefix = "/api/v1"

app.include_router(
    accounts.router, prefix=f"{api_version_prefix}/accounts", tags=["accounts"]
)
app.include_router(
    catalog.router, prefix=f"{api_version_prefix}/cinema", tags=["cinema"]
)
app.include_router(
    moderator.router, prefix=f"{api_version_prefix}/cinema", tags=["cinema"]
)
app.include_router(comments.router, prefix=f"{api_version_prefix}", tags=["comments"])
app.include_router(
    favorites.router, prefix=f"{api_version_prefix}/favorites", tags=["favorites"]
)
app.include_router(
    ratings.router, prefix=f"{api_version_prefix}/cinema/movies", tags=["ratings"]
)
