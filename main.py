"""
FastAPI application entry point.

This module initializes the FastAPI application and includes all the necessary routes
for contacts, users, authentication, and utility endpoints. It also configures middleware for handling CORS
and rate-limiting errors.

Functions:
    - rate_limit_handler: Handles rate limit exceeded errors by returning a custom error message.
"""

from fastapi import FastAPI, Request, status
from slowapi.errors import RateLimitExceeded
from src.api import contacts, utils, auth, users
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# from src.database.redis import init_redis, close_redis
from contextlib import asynccontextmanager


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await init_redis()
#     yield
#     await close_redis()


# app = FastAPI(lifespan=lifespan)
app = FastAPI()



# @app.on_event("startup")
# async def startup():
#     await init_redis()
#
# @app.on_event("shutdown")
# async def shutdown():
#     await close_redis()

origins = [
    "http://localhost:8000"
    ]

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
        Handles rate limit exceeded errors.

        This function returns a custom error message when the user exceeds the rate limit for requests.

        Args:
            request (Request): The incoming request that triggered the rate limit error.
            exc (RateLimitExceeded): The exception raised when the rate limit is exceeded.

        Returns:
            JSONResponse: A response with a status code of 429 and an error message.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000)

