"""PIL Services - Assessment application module."""
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel


class Announcement(BaseModel):
    guid: int
    title: str
    description: str
    date: str


app = FastAPI()


@app.post("/announcements/")
def post_announcements(announcement: Announcement):
    # write data to dynamodb
    data = []
    print(announcement)
    if data:
        return {"status": 200, "message": "Successfully saved data into table."}


@app.get("/")
def root():
    return {"message": "Hi"}


@app.get("/announcements/")
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
        return announcement
    else:
        raise HTTPException(status_code=404, detail="Item not found")


handler = Mangum(app=app)
