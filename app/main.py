import time
from typing import Union, Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session

from . import models, schemas, utils
import config
from .database import engine, get_db

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


@app.get("/posts", response_model=List[schemas.Post])
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


@app.get("/posts/{id}", response_model=schemas.Post)
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


@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = db.query(models.Post).filter(models.Post.id == id)

    post = new_post.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")

    new_post.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return new_post.first()


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_pass = utils.hashed(user.password)
    user.password = hashed_pass
    res = models.User(**user.dict())
    db.add(res)
    db.commit()
    db.refresh(res)
    return res


@app.get("/users/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    res = db.query(models.User).filter(models.User.id == id).first()
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    return res
