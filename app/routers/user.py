from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/users"
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_pass = utils.hashed(user.password)
    user.password = hashed_pass
    res = models.User(**user.dict())
    db.add(res)
    db.commit()
    db.refresh(res)
    return res


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    res = db.query(models.User).filter(models.User.id == id).first()
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    return res
