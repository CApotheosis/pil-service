"""PIL Services - Assessment application module."""
import uuid

from datetime import datetime
from typing import Optional

import boto3

from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel

from src.integrations.db import DBStorageAccess

app = FastAPI()
resource = boto3.resource("dynamodb")
dynamodb = DBStorageAccess(resource)


class Announcement(BaseModel):
    guid: Optional[int] = None
    title: str
    description: str
    created_date: Optional[str] = None


@app.post("/announcements/")
def post_announcement(announcement: Announcement):
    announcement.guid = uuid.uuid4().hex
    announcement.created_date = str(datetime.now())

    dynamodb.save_announcement(dict(
            {
                "guid": announcement.guid,
                "title": announcement.title,
                "description": announcement.description,
                "created_date": announcement.created_date,
            }
        )
    )

    return announcement


@app.get("/")
def root():
    return {"status": 200, "message": "application is running"}


@app.get("/announcements")
def get_announcements(page: int = 1):
    items_to_show_per_request = 10
    announcements = dynamodb.get_announcements(page, items_to_show_per_request)
    announcements_length = len(announcements)

    return {
        "announcements": announcements,
        "max_count": announcements_length,
        "items_per_request": items_to_show_per_request,
    }


@app.get("/announcements/{announcement_guid}")
def get_announcement_property(announcement_guid: str):
    announcement = dynamodb.get_announcement("guid", announcement_guid)

    return announcement


handler = Mangum(app=app)
