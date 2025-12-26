from fastapi import FastAPI

from src.routes import accounts, movies

app = FastAPI(
    title="Online Cinema API",
    description="A simple API for management movies and users in online cinema",
)

api_version_prefix = "/api/v1"

app.include_router(accounts.router, prefix=f"{api_version_prefix}/accounts", tags=["accounts"])
app.include_router(movies.router, prefix=f"{api_version_prefix}/movies", tags=["movies"])
