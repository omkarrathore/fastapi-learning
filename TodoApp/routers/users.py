import sys
sys.path.append('../')

from fastapi import Depends,status,APIRouter
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from pydantic import BaseModel,Field
#from typing import Optional
from .auth import get_current_user, get_user_exception, get_password_hash,verify_password
#from passlib.context import CryptContext
#from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404:{"description":"Not Found"}}
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class userVerification(BaseModel):
    username:str
    password:str
    new_password:str

@router.get("/")
async def read_all(db:Session=Depends(get_db)):
    return db.query(models.Users).all()
    
@router.get("/userById")
async def read_user_by_query_id(user_id:int, db:Session=Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user_model is not None:
        return user_model
    else:
        return "Invalid user id"
    
@router.get("/{user_id}")
async def read_user_by_path_id(user_id:int, db:Session=Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user_model is not None:
        return user_model
    else:
        return "Invalid user id"

@router.put("/update_password")
async def update_password(user_verification:userVerification, usr:dict=Depends(get_current_user), db:Session=Depends(get_db)):
    if usr is None:
        return get_user_exception()
    print(usr)
    user = db.query(models.Users).filter(models.Users.id == usr.get('id')).first()
    if user is not None:
        if user_verification.username == user.username and \
            verify_password(user_verification.password,user.hashed_password):
            user.hashed_password = get_password_hash(new_password)
            db.add(user)
            db.commit()
            return sucessful_response(200)
    return "Invalid user or request"

@router.delete("/delete_user")
async def update_password( usr:dict=Depends(get_current_user), db:Session=Depends(get_db)):
    print(usr)
    if usr is not None:
        user = db.query(models.Users).filter(models.Users.id == usr.get('id')).first()
        if user is not None:
            db.query(models.Users).filter(models.Users.id == usr.get('id')).delete()
            db.query(models.Todos).filter(models.Todos.owner_id == usr.get('id')).delete()
            db.commit()
            return sucessful_response(204)
        return get_user_exception()
    else:
        return get_user_exception()

def sucessful_response(status_code: int):
    return {
        'status':status_code,
        'transaction':'Sucessful'
    }

