from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schemas.Post])
def posts_get(db: Session = Depends(get_db)):
    res = db.query(models.Post).all()
    return res


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    res = models.Post(**post.dict())
    db.add(res)
    db.commit()
    db.refresh(res)
    return res


@router.get("/{id}", response_model=schemas.Post)
def get_posts_id(id: int, db: Session = Depends(get_db)):
    res = db.query(models.Post).filter(models.Post.id == id).first()
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    return res


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = db.query(models.Post).filter(models.Post.id == id)

    post = new_post.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")

    new_post.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return new_post.first()

