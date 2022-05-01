# necessary imports
from typing import List
from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, status

from . import models, schemas, utils
from .database import engine, get_db



models.Base.metadata.create_all(bind=engine)

# create a FastAPI app instance
app = FastAPI()

# create the root route
@app.get("/")
def read_root():
    return {"Welcome to Personal Finance API": "Get our app at APP_URL"}, status.HTTP_200_OK


# create a route to return one user
@app.get("/users/{email}", status_code=200)
async def read_user(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email.lower()).first()
    if user is None:
       return {"error": "User not found"}, status.HTTP_404_NOT_FOUND
    return {"Message": "User is already registered"}, status.HTTP_200_OK


# create a route to add a user
@app.post("/users", status_code=201, response_model=schemas.UserCreate)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    checkuser = (db.query(models.User)
        .filter(models.User.email == user.email.lower())
        .first()
    )
    if checkuser:
        return {"error": "User already exists"}, status.HTTP_400_BAD_REQUEST
    hashed_password = utils.hash_context(user.password)
    new_user = models.User(email=user.email.lower(), password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"Message": "User created successfully"}, status.HTTP_201_CREATED


# create a route to return all transactions from a user
@app.get("/transactions/{user_id}" , status_code=200)
async def read_transactions(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(models.Transaction.user_id == user_id).all()
    return {"data": transactions}, status.HTTP_200_OK


# create a route to add a transaction
@app.post("/transactions", status_code=201)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(models.User)
        .filter(
            models.User.user_id == transaction.user_id,
        )
        .first()
    )
    if existing_user is None:
        return {"error": "There is no user with that id"}, status.HTTP_404_NOT_FOUND
    new_transaction = models.Transaction(**transaction.dict())
    db.add(new_transaction)
    db.commit()
    transaction = (
        db.query(models.Transaction)
        .order_by(models.Transaction.transaction_id.desc())
        .filter(
            models.Transaction.transaction_name == transaction.transaction_name
            and models.Transaction.user_id == transaction.user_id,
        )
        .first()
    )
    return {"data": transaction}, status.HTTP_201_CREATED


# create a route to move funds from one account to another
@app.post("/move_funds", status_code=201)
async def move_funds(
    user_id: int,
    transaction_value: float,
    transaction_date: str,
    account_type: str,
    db: Session = Depends(get_db),
):
    # check if user exists
    existing_user = (
        db.query(models.User)
        .filter(
            models.User.user_id == user_id,
        )
        .first()
    )
    if existing_user is None:
        return {"error": "There is no user with that id"}, status.HTTP_404_NOT_FOUND

    # defining the direction of the transaction
    if account_type == "main":
        account_debit = "savings"
        account_credit = "main"
    else:
        account_debit = "main"
        account_credit = "savings"

    # get the origin account balance
    main_account_credit = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == user_id,
            models.Transaction.account_type == account_debit,
            models.Transaction.transaction_type == "credit",
        )
        .all()
    )
    # get the total credit amount of origin account
    main_account_credit_total = 0
    for transaction in main_account_credit:
        main_account_credit_total += transaction.transaction_value

    # get the origin account debits
    main_account_debit = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == user_id,
            models.Transaction.account_type == account_debit,
            models.Transaction.transaction_type == "debit",
        )
        .all()
    )

    # get the total debit amount of origin account
    main_account_debit_total = 0
    for transaction in main_account_debit:
        main_account_debit_total += transaction.transaction_value

    main_account_balance = main_account_credit_total - main_account_debit_total

    # check if user has enough funds to move funds
    if main_account_balance < transaction_value:
        return {"error": "Not enough funds to move funds"}, status.HTTP_400_BAD_REQUEST

    # debit transaction
    debit_transaction = models.Transaction(
        user_id=user_id,
        transaction_name="Transfer funds",
        transaction_category="transfer",
        transaction_type="debit",
        transaction_value=transaction_value,
        transaction_date=transaction_date,
        account_type=account_debit,
    )
    db.add(debit_transaction)
    db.commit()

    # credit transaction
    credit_transaction = models.Transaction(
        user_id=user_id,
        transaction_name="Receive funds",
        transaction_category="transfer",
        transaction_type="credit",
        transaction_value=transaction_value,
        transaction_date=transaction_date,
        account_type=account_credit,
    )
    db.add(credit_transaction)
    db.commit()
    transaction_credit_registered = (
        db.query(models.Transaction)
        .order_by(models.Transaction.transaction_id.desc())
        .filter(
            models.Transaction.transaction_category == "Transfer"
            and models.Transaction.user_id == user_id,
        )
        .first()
    )
    return {
        "Message": "Funds moved successfully",
        "data": transaction_credit_registered,
    }, status.HTTP_201_CREATED


# create a route to return all suggestions
@app.get("/suggestions")
async def read_suggestions(db: Session = Depends(get_db)):
    suggestions = db.query(models.Suggestion).all()
    return {"data": suggestions}, status.HTTP_200_OK


# create a route to add a suggestion
@app.post("/suggestions", status_code=201)
async def create_suggestion(
    category: str,
    description: str,
    db: Session = Depends(get_db),
):
    suggestion = models.Suggestion(
        category=category,
        description=description,
    )
    db.add(suggestion)
    db.commit()
    suggestion = (
        db.query(models.Suggestion)
        .order_by(models.Suggestion.suggestion_id.desc())
        .filter(
            models.Suggestion.category == category,
        )
        .first()
    )
    return {"data": suggestion}, status.HTTP_201_CREATED
