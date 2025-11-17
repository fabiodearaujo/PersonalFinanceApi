# necessary imports
from app import models, oauth2, schemas, utils
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


# route to add a user
@router.post("/create", status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # check if the user already exists
    check_user = (
        db.query(models.User).filter(models.User.email == user.email.lower()).first()
    )
    if check_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists."
        )

    # check if password is strong enough
    if not utils.check_password_strength(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password is not strong enough. (Minimum of 8 characters, "
                "upper and lower case, number and a special symbol.)"
            ),
        )

    # hash the password
    hashed_password = utils.hash_context(user.password)

    # create the user
    new_user = models.User(email=user.email.lower(), password=hashed_password)
    db.add(new_user)
    db.commit()

    # initialize the user's main and savings accounts
    user_created = (
        db.query(models.User).filter(models.User.email == user.email.lower()).first()
    )

    new_main_account = schemas.TransactionCreate(
        user_id=user_created.user_id,
        transaction_name="Main account opening",
        transaction_category="Initial balance",
        transaction_type="credit",
        transaction_value=0,
        transaction_date=utils.get_current_date(),
        account_type="main",
    )
    new_main_transaction = models.Transaction(**new_main_account.model_dump())

    new_savings_account = schemas.TransactionCreate(
        user_id=user_created.user_id,
        transaction_name="Savings account opening",
        transaction_category="Initial balance",
        transaction_type="credit",
        transaction_value=0,
        transaction_date=utils.get_current_date(),
        account_type="savings",
    )
    new_savings_transaction = models.Transaction(**new_savings_account.model_dump())

    db.add(new_main_transaction)
    db.add(new_savings_transaction)
    db.commit()

    return {"Message": "User created successfully."}


# route to get a user
@router.get("/my_user", status_code=200)
def get_my_user(
    user_auth: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    # get the user from the database
    user = (
        db.query(models.User).filter(models.User.user_id == user_auth.user_id).first()
    )
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    
    # Return user data using MyUser schema
    return schemas.MyUser(
        user_id=user.user_id,
        email=user.email
    )


# route to update a user details
@router.put("/email", status_code=200)
def update_user_email(
    user: schemas.UserUpdateEmail,
    db: Session = Depends(get_db),
    user_auth: models.User = Depends(oauth2.get_current_user),
):
    # verify if it is the correct user
    if user.user_id != user_auth.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=("You are not authorized to update this user."),
        )

    # check if the user already exists
    check_user_email = (
        db.query(models.User).filter(models.User.email == user.email.lower()).first()
    )
    if check_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists."
        )

    # return user details
    check_user = (
        db.query(models.User).filter(models.User.user_id == user.user_id).first()
    )

    # update the user email information
    user.email = user.email.lower()

    # verify if password is correct
    verify_password = utils.verify_context(user.password, check_user.password)
    if not verify_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials."
        )

    # update the user email
    check_user.email = user.email
    db.commit()
    return {"Message": "User updated successfully."}


# route to update a user password
@router.put("/password", status_code=200)
def update_user_password(
    user: schemas.UserUpdatePassword,
    db: Session = Depends(get_db),
    user_auth: models.User = Depends(oauth2.get_current_user),
):
    # verify if it is the correct user
    if user.user_id != user_auth.user_id:
        return {
            "error": "You are not authorized to update this user."
        }, status.HTTP_401_UNAUTHORIZED

    # check if password is strong enough
    if not utils.check_password_strength(user.new_password):
        return {
            "error": (
                "Password is not strong enough. (Minimum of 8 characters,"
                " upper and lower case, number and a special symbol.)"
            )
        }, status.HTTP_400_BAD_REQUEST

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
    user_auth: models.User = Depends(oauth2.get_current_user),
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
