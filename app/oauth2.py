# necessary imports to setup the oauth2
from datetime import datetime, timedelta

from app import database, models, schemas
# from decouple import config
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")

# set the emvoronment variables for the token
# SECRET_KEY = config("SECRET_KEY")
# ALGORITHM = config("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

# function to create a token
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# function to verify the token
def verify_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        decoded_id: str = payload.get("user_id")
        if decoded_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_id=decoded_id)
    except JWTError:
        raise credentials_exception
    return token_data


# function to get the user id from the token
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    verified_token = verify_access_token(token, credentials_exception)
    user = (
        db.query(models.User)
        .filter(models.User.user_id == verified_token.user_id)
        .first()
    )
    return user
