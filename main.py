from fastapi import FastAPI

from typing import Optional

app = FastAPI()


@app.get("/blog")
def index(limit=10, published: bool = True, sort: Optional[str] = None):
    if published:
        return {"data": f"published {limit} show db"}
    else:
        return {"data": f"NOT published {limit} show db"}


@app.get("/blog/unpublished")
def unpublished():
    return {"data": "unpublished blog"}


@app.get("/blog/{blog_id}")
def about(blog_id: int):
    return {"data": 'ads'}


@app.get("/blog/{blog_id}/comments")
def comments():
    return {"data": {"1", "2"}}
