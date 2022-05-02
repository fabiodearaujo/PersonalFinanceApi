# necessary imports
from fastapi import APIRouter, Depends, status
from pydantic import EmailStr
from requests import Session

from app import models, schemas, utils
from app.database import get_db

router = APIRouter()

# route to return one user
@router.get("/users/{email}", status_code=200)
async def read_user(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email.lower()).first()
    if user is None:
        return {"error": "User not found"}, status.HTTP_404_NOT_FOUND
    return {"Message": "User is already registered"}, status.HTTP_200_OK


# route to add a user
@router.post("/users", status_code=201)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # check if the user already exists
    check_user = (
        db.query(models.User).filter(models.User.email == user.email.lower()).first()
    )
    if check_user:
        return {"error": "User already exists"}, status.HTTP_400_BAD_REQUEST

    # hash the password
    hashed_password = utils.hash_context(user.password)

    # create the user
    new_user = models.User(email=user.email.lower(), password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"Message": "User created successfully"}, status.HTTP_201_CREATED


# route to update a user details
@router.put("/users/{user_id}", status_code=200)
async def update_user_email(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):

    # check if the user already exists
    check_user_email = (db.query(models.User)
        .filter(models.User.email == user.email.lower())
        .first()
    )
    if check_user_email:
        return {"error": "User already exists"}, status.HTTP_400_BAD_REQUEST

    # return user details
    check_user = db.query(models.User).filter(models.User.user_id == user_id).first()

    # update the user email information
    user.email = user.email.lower()

    # verify if password is correct
    verify_password = utils.verify_context(user.password, check_user.password)
    if not verify_password:
        return {"error": "Incorrect password"}, status.HTTP_400_BAD_REQUEST

    # update the user email
    check_user.email = user.email
    db.commit()
    return {"Message": "User updated successfully"}, status.HTTP_200_OK


# route to update a user password
@router.put("/users/password/{user_id}", status_code=200)
async def update_user_password(user_id: int, user: schemas.UserUpdatePassword, db: Session = Depends(get_db)):

    # return user details
    check_user = db.query(models.User).filter(models.User.user_id == user_id).first()

    # verify if password is correct
    verify_password = utils.verify_context(user.password, check_user.password)
    if not verify_password:
        return {"error": "Incorrect password"}, status.HTTP_400_BAD_REQUEST

    # hash the new password
    hashed_password = utils.hash_context(user.new_password)

    # update the user password
    check_user.password = hashed_password
    db.commit()
    return {"Message": "User password updated successfully"}, status.HTTP_200_OK


# route to delete a user
@router.delete("/users/{user_id}", status_code=200)
async def delete_user(user_id: int, confirm: str, db: Session = Depends(get_db)):
    # find the user to be deleted
    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    #check confirmation
    if confirm.lower() == "n":
        return {"error": "User not deleted."}, status.HTTP_400_BAD_REQUEST

    # delete the user
    db.delete(user)
    db.commit()
    return {"Message": "User deleted successfully"}, status.HTTP_200_OK
