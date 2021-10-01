"""PIL Services - Assessment application module."""
from datetime import datetime
from time import time_ns
from typing import Optional

import boto3
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel


class Announcement(BaseModel):
    guid: Optional[int] = None
    title: str
    description: str
    created_date: Optional[str] = None


app = FastAPI()
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Announcements")


@app.post("/announcements/")
def post_announcement(announcement: Announcement):
    announcement.guid = time_ns()
    announcement.created_date = str(datetime.fromtimestamp(announcement.guid / 10 ** 9).date())

    table.put_item(
        Item={
            "guid": announcement.guid,
            "title": announcement.title,
            "description": announcement.description,
            "created_date": announcement.created_date,
        }
    )

    return announcement


@app.get("/")
def root():
    return {"status": 200, "message": "application is running"}


@app.get("/announcements")
def get_announcements(page: int = 1):
    response = table.scan()
    announcements = response["Items"]
    announcements_length = len(announcements)
    items_to_show = 10

    if page > 1:
        start = (page - 1) * items_to_show
        end = start + items_to_show
        return {
            "announcements": announcements[start:end],
            "max_count": announcements_length,
            "items_per_page": items_to_show,
        }
    else:
        return {
            "announcements": announcements[:items_to_show],
            "max_count": announcements_length,
            "items_per_page": items_to_show,
        }


@app.get("/announcements/{announcement_guid}")
def get_announcement_property(announcement_guid: int):
    response = table.scan()
    announcements = response["Items"]

    if announcement := list(filter(lambda item: item["guid"] == announcement_guid, announcements)):
        return announcement[0]
    else:
        raise HTTPException(status_code=404, detail="Item not found")


handler = Mangum(app=app)
