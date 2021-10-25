"""PIL Services - Assessment application module."""
import uuid
import logging

from datetime import datetime
from typing import Optional

import boto3

from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel

from integrations.db import DBStorageAccess

app = FastAPI()
resource = boto3.resource("dynamodb")
dynamodb = DBStorageAccess(resource)
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger("pil-services")
logger.setLevel(logging.INFO)


class Announcement(BaseModel):
    guid: Optional[int] = None
    title: str
    description: str
    created_date: Optional[str] = None


@app.post("/announcements/")
def post_announcement(announcement: Announcement):
    announcement.guid = uuid.uuid4().hex
    announcement.created_date = str(datetime.now())

    try:
        dynamodb.save_announcement(dict(
                {
                    "guid": announcement.guid,
                    "title": announcement.title,
                    "description": announcement.description,
                    "created_date": announcement.created_date,
                }
            )
        )
    except Exception:
        logger.exception("Item creation failed.")
    else:
        logger.info("Successfully created item.")

    return announcement


@app.get("/")
def root():
    logger.info("Working", {"status": 200, "message": "application is running"})
    return {"status": 200, "message": "application is running"}


@app.get("/announcements")
def get_announcements(page: int = 1):
    items_to_show_per_request = 10
    announcements = dynamodb.get_announcements(page, items_to_show_per_request)
    announcements_length = len(announcements)

    if announcements:
        logger.info("Got items.")

        return {
            "announcements": announcements,
            "max_count": announcements_length,
            "items_per_request": items_to_show_per_request,
        }
    else:
        logger.exception("Failed to fetch items or got an empty list.")

        return announcements


@app.get("/announcements/{announcement_guid}")
def get_announcement_property(announcement_guid: str):
    announcement = dynamodb.get_announcement("guid", announcement_guid)

    return announcement


handler = Mangum(app=app)
