from typing import Union, Optional

from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session

from . import models
import config
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


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
    cursor.execute("SELECT * FROM posts;")
    res = cursor.fetchall()
    return {"data": res}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute("""
    INSERT INTO posts (title, content) 
    VALUES (%(title)s, %(content)s) RETURNING *;""", {
        'title': post.title,
        'content': post.content,
        }
    )
    res = cursor.fetchone()
    conn.commit()
    return {"New post!": res}


@app.get("/posts/latest")
def get_latest_post():
    cursor.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1;")
    res = cursor.fetchone()
    return {"Latest post": res}


@app.get("/posts/{id}")
def get_posts_id(id: int, response: Response):
    cursor.execute("SELECT * FROM posts WHERE id = %(id)s;", {
        'id': id
    })
    res = cursor.fetchone()
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    return {"Your post": res}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""
        DELETE FROM posts WHERE id = %(id)s RETURNING *;""", {
        'id': id,
        }
    )
    res = cursor.fetchone()
    conn.commit()
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="post does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""
        UPDATE posts SET title = %(title)s, content = %(content)s 
        WHERE id = %(id)s RETURNING *;""", {
            'id': id,
            'title': post.title,
            'content': post.content,
        }
    )
    res = cursor.fetchone()
    conn.commit()
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="post does not exist")

    return {"Updated": res}
