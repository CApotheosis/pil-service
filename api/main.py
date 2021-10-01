"""PIL Services - Assessment application module."""
from datetime import datetime
from time import time_ns
from typing import Optional

from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel


class Announcement(BaseModel):
    guid: Optional[int] = None
    title: str
    description: str
    created_date: Optional[str] = None


app = FastAPI()


@app.post("/announcements/")
def post_announcement(announcement: Announcement):
    # write data to dynamodb
    announcement.guid = time_ns()
    announcement.created_date = str(datetime.fromtimestamp(announcement.guid / 10 ** 9).date())
    print("announcement", announcement)

    return announcement


@app.get("/")
def root():
    return {"status": 200, "message": "application is running"}


@app.get("/announcements")
def get_announcements(page: int = 1):
    # get elements from db
    announcements = [
        {
            "guid": 21312421,
            "title": "some title 1",
            "description": "some description 1",
            "date": "some date 1",
        },
        {
            "guid": 421321321,
            "title": "some title 2",
            "description": "some description 2",
            "date": "some date 2",
        },
        {
            "guid": 43123122765,
            "title": "some title 3",
            "description": "some description 3",
            "date": "some date 3",
        },
    ]
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
    announcements = [
        {
            "guid": 21312421,
            "title": "some title 1",
            "description": "some description 1",
            "date": "some date 1",
        },
        {
            "guid": 421321321,
            "title": "some title 2",
            "description": "some description 2",
            "date": "some date 2",
        },
        {
            "guid": 43123122765,
            "title": "some title 3",
            "description": "some description 3",
            "date": "some date 3",
        },
    ]
    if announcement := list(filter(lambda item: item["guid"] == announcement_guid, announcements)):
        return announcement[0]
    else:
        raise HTTPException(status_code=404, detail="Item not found")


handler = Mangum(app=app)
