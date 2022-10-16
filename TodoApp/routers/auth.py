import sys
sys.path.append('../')

from fastapi import Depends,HTTPException,status,APIRouter #,FastAPI
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
import models
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime,timedelta
from jose import jwt,JWTError

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Createuser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password:str

models.Base.metadata.create_all(bind=engine)
bcrypt_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

#app = FastAPI()
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user":"Not authorized"}}
)

SECRET_KEY="omkarOm$a%"
ALGORITHM="HS256"


def get_password_hash(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password,hashed_password):
    return bcrypt_context.verify(plain_password,hashed_password)

def authenticate_user(username:str,password:str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False
    if not verify_password(password,user.hashed_password):
        return False
    return user

def create_access_token(username:str,user_id:int, expiers_delta:Optional[timedelta]=None):
    encode = {"sub":username,"id":user_id}
    if expiers_delta:
        expier = datetime.utcnow()+expiers_delta
    else:
        expier = datetime.utcnow()+timedelta(minutes=15)
    encode.update({"exp":expier})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token:str = Depends(oauth2_bearer)):
    try:
        print("Inside get current user")
        print(token)
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        print(payload)
        username:str = payload.get("sub")
        user_id:str = payload.get("id")
        if username is None or user_id is None:
            raise get_user_exception()
        return {"username":username,"id":user_id}
    except JWTError:
            raise get_user_exception()

@router.post("/create/user")
async def create_new_user(create_user:Createuser,db:Session=Depends(get_db)):
    create_user_model = models.Users()
    create_user_model.email = create_user.email
    create_user_model.username = create_user.username
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name
    create_user_model.hashed_password = get_password_hash(create_user.password)
    create_user_model.is_active = True
    db.add(create_user_model)
    db.commit()
    #return create_user_model

@router.post("/token")
async def login_for_access_token(form:OAuth2PasswordRequestForm = Depends(), db:Session=Depends(get_db)):
    user = authenticate_user(form.username,form.password,db)
    if not user:
        raise token_exception()
    token_expiers = timedelta(minutes=20)
    token = create_access_token(user.username,user.id,
                                expiers_delta=token_expiers)
    return{"token":token}

#Exception
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate the credentials",
        headers={"WWW-AUTHENTICATE":"Bearer"}
    )
    return credentials_exception

def token_exception():
    token_exception_reponse= HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-AUTHENTICATE":"Bearer"}
    )
    return token_exception_reponse

