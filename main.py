from typing import Union, Optional

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_posts = [{"title1": "title1", "content": "content1", "id": 1},
            {"title2": "title2", "content": "content2", "id": 2}]


def find_id(id):
    for p in my_posts:
        if p["id"] == id:
            return p


@app.get("/")
def hello():
    return {"Hello": "World"}


@app.get("/posts")
def posts_get():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    new_post = post.dict()
    new_post['id'] = randrange(1, 100000)
    my_posts.append(new_post)
    return {"data": new_post}


@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[-1]
    return {"Your post": post}


@app.get("/posts/{id}")
def get_posts_id(id: int, response: Response):

    post = find_id(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Your {id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND
    return {"Your post": post}





