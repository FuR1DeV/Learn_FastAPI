from typing import Union, Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session

from app import models, schemas
import config
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(host=config.HOST,
                                database=config.DATABASE,
                                user=config.POSTGRESQL_USER,
                                password=config.POSTGRESQL_PASSWORD,
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Databases connection successful")
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
def posts_get(db: Session = Depends(get_db)):
    res = db.query(models.Post).all()
    return res


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    res = models.Post(**post.dict())
    db.add(res)
    db.commit()
    db.refresh(res)
    return res


@app.get("/posts/{id}")
def get_posts_id(id: int, db: Session = Depends(get_db)):
    res = db.query(models.Post).filter(models.Post.id == id).first()
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    return res


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = db.query(models.Post).filter(models.Post.id == id)

    post = new_post.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")

    new_post.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return new_post.first()
