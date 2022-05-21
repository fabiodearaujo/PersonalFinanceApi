# necessary imports
from app import models, oauth2, schemas, utils
from app.database import get_db
from fastapi import APIRouter, Depends, status
from pyparsing import DictType
from sqlalchemy.orm import Session

router = APIRouter()


#route to return own user
@router.get("/users/me", response_model=schemas.User)
async def read_own_user(current_user: models.User = Depends(utils.get_current_user)):
    return current_user


# route to add a user
@router.post("/create", status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # check if the user already exists
    check_user = (
        db.query(models.User).filter(models.User.email == user.email.lower()).first()
    )
    if check_user:
        return {"error": "User already exists."}, status.HTTP_400_BAD_REQUEST

    # hash the password
    hashed_password = utils.hash_context(user.password)

    # create the user
    new_user = models.User(email=user.email.lower(), password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"Message": "User created successfully."}, status.HTTP_201_CREATED


# route to update a user details
@router.put("/email", status_code=200)
def update_user_email(
    user: schemas.UserUpdateEmail,
    db: Session = Depends(get_db),
    user_auth: DictType = Depends(oauth2.get_current_user),
):
    # verify if it is the correct user
    if user.user_id != user_auth.user_id:
        return {
            "error": "You are not authorized to update this user."
        }, status.HTTP_401_UNAUTHORIZED

    # check if the user already exists
    check_user_email = (
        db.query(models.User).filter(models.User.email == user.email.lower()).first()
    )
    if check_user_email:
        return {"error": "User already exists."}, status.HTTP_400_BAD_REQUEST

    # return user details
    check_user = (
        db.query(models.User).filter(models.User.user_id == user.user_id).first()
    )

    # update the user email information
    user.email = user.email.lower()

    # verify if password is correct
    verify_password = utils.verify_context(user.password, check_user.password)
    if not verify_password:
        return {"error": "Incorrect credentials."}, status.HTTP_400_BAD_REQUEST

    # update the user email
    check_user.email = user.email
    db.commit()
    return {"Message": "User updated successfully."}, status.HTTP_200_OK


# route to update a user password
@router.put("/password", status_code=200)
def update_user_password(
    user: schemas.UserUpdatePassword,
    db: Session = Depends(get_db),
    user_auth: DictType = Depends(oauth2.get_current_user),
):
    # verify if it is the correct user
    if user.user_id != user_auth.user_id:
        return {
            "error": "You are not authorized to update this user."
        }, status.HTTP_401_UNAUTHORIZED

    # return user details
    check_user = (
        db.query(models.User).filter(models.User.user_id == user.user_id).first()
    )

    # verify if password is correct
    verify_password = utils.verify_context(user.password, check_user.password)
    if not verify_password:
        return {"error": "Credentials are incorrect."}, status.HTTP_400_BAD_REQUEST

    # hash the new password
    hashed_password = utils.hash_context(user.new_password)

    # update the user password
    check_user.password = hashed_password
    db.commit()
    return {"Message": "User password updated successfully."}, status.HTTP_200_OK


# route to delete a user
@router.delete("/delete", status_code=200)
def delete_user(
    user: schemas.UserDelete,
    db: Session = Depends(get_db),
    user_auth: DictType = Depends(oauth2.get_current_user),
):
    # find the user to be deleted
    user_to_delete = (
        db.query(models.User).filter(models.User.user_id == user.user_id).first()
    )

    # verify if password is correct
    verify_password = utils.verify_context(user.password, user_to_delete.password)
    if not verify_password:
        return {"error": "Credentials does not match."}, status.HTTP_400_BAD_REQUEST

    # verify if it is the correct user
    if user.user_id != user_auth.user_id:
        return {
            "error": "You are not authorized to delete this user."
        }, status.HTTP_401_UNAUTHORIZED

    # check confirmation
    if user.confirm is not True:
        return {
            "error": "User not deleted. Not Confirmed."
        }, status.HTTP_400_BAD_REQUEST

    # delete the user
    db.delete(user_to_delete)
    db.commit()
    return {"Message": "User deleted successfully."}, status.HTTP_200_OK
