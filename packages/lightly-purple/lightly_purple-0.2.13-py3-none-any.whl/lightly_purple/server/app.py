"""This module contains the FastAPI app configuration."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import DataError, IntegrityError, OperationalError
from sqlmodel import Session
from typing_extensions import Annotated

from lightly_purple.dataset.env import PURPLE_DEBUG
from lightly_purple.server.cache import StaticFilesCache
from lightly_purple.server.db import db_manager
from lightly_purple.server.routes import healthz, webapp
from lightly_purple.server.routes.api import (
    annotation,
    annotation_label,
    dataset,
    dataset_tag,
    sample,
)
from lightly_purple.server.routes.api.status import (
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_CONFLICT,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
)

SessionDep = Annotated[Session, Depends(db_manager.session)]


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan context for initializing and cleaning up resources."""
    yield


if PURPLE_DEBUG == "True":
    import logging

    logging.basicConfig()
    logger = logging.getLogger("sqlalchemy.engine")
    logger.setLevel(logging.DEBUG)

"""Create the FastAPI app."""
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/images",
    StaticFilesCache(directory="/"),
    "images",
)


@app.exception_handler(IntegrityError)
async def _integrity_error_handler(_request, _exc):
    return HTTPException(
        status_code=HTTP_STATUS_CONFLICT, detail="Database constraint violated."
    )


@app.exception_handler(DataError)
async def _data_error_handler(_request, _exc):
    return HTTPException(
        status_code=HTTP_STATUS_BAD_REQUEST, detail="Invalid data provided."
    )


@app.exception_handler(OperationalError)
async def _operational_error_handler(_request, _exc):
    return HTTPException(
        status_code=HTTP_STATUS_INTERNAL_SERVER_ERROR,
        detail="Database operation failed.",
    )


# api routes
app.include_router(dataset.dataset_router, prefix="/api")
app.include_router(dataset_tag.tag_router, prefix="/api")
app.include_router(sample.samples_router, prefix="/api")
app.include_router(annotation_label.annotations_label_router, prefix="/api")
app.include_router(annotation.annotations_router, prefix="/api")


# health status check
app.include_router(healthz.health_router)

# webapp routes
app.include_router(webapp.app_router)
