from typing import Union, Optional

from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_posts = [{"title": "title1", "content": "content1", "id": 1}]


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


@app.post("/posts")
def create_post(post: Post):
    new_post = post.dict()
    new_post['id'] = randrange(1, 100000)
    my_posts.append(new_post)
    return {"data": new_post}


@app.get("/posts/{id}")
def get_posts_id(id):
    post = find_id(int(id))
    return {"Your post": post}
