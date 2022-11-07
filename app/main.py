from typing import Union, Optional

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

import config

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

while True:
    try:
        conn = psycopg2.connect(host=config.HOST,
                                database=config.DATABASE,
                                user=config.POSTGRESQL_USER,
                                password=config.POSTGRESQL_PASSWORD,
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Databases connection succesfull")
        break
    except Exception as err:
        print(f"Connect failed | error - {err}")
        time.sleep(2)

my_posts = [{"title": "Super 1", "content": "content of post 1", "id": 1},
            {"title": "Super 2", "content": "content of post 2", "id": 2}]


def find_id(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_id_index(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


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
    return {"Your post": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_id_index(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="post does not exist")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_id_index(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="post does not exist")
    new_post = post.dict()
    new_post["id"] = id
    my_posts[index] = new_post
    return {"Updated": new_post}
