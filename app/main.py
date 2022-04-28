# necessary imports
import time

import psycopg2
from decouple import config
from fastapi import Depends, FastAPI
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session

from .database import engine, get_db
from .models import User, Transaction, Suggestion, Base

Base.metadata.create_all(bind=engine)

# create a FastAPI app instance
app = FastAPI()

# configuring the environment variables
DB_USER = config("DB_USER")
DB_NAME = config("DB_NAME")
DB_ADDRESS = config("DB_ADDRESS")
DB_PASSWORD = config("DB_PASSWORD")

# database connection
while True:
    try:
        conn = psycopg2.connect(
            host=DB_ADDRESS,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Connected to database")
        break
    except Exception as e:
        print("Unable to connect to database")
        print("Error: ", e)
        time.sleep(5)


# create the root route
@app.get("/")
def read_root():
    return {"Welcome to Personal Finance API": "Get our app at APP_URL"}


# create a route to return one user
@app.get("/users/{email}")
def read_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return {"data": user} if user else {"error": "User not found"}


# create a route to add a user
@app.post("/users", status_code=201)
def create_user(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return {"error": "User already exists"}
    user = User(email=email, password=password)
    db.add(user)
    db.commit()
    user = db.query(User).filter(User.email == email).first()
    return {"data": user}


# create a route to return all transactions from a user
@app.get("/transactions/{user_id}")
def read_transactions(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return {"data": transactions}


# create a route to add a transaction
@app.post("/transactions", status_code=201)
def create_transaction(
    user_id: int,
    transaction_name: str,
    transaction_category: str,
    transaction_type: str,
    transaction_value: float,
    transaction_date: str,
    account_type: str,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(
            User.user_id == user_id,
        )
        .first()
    )
    if existing_user is None:
        return {"error": "There is no user with that id"}
    transaction = Transaction(
        user_id=user_id,
        transaction_name=transaction_name,
        transaction_category=transaction_category,
        transaction_type=transaction_type,
        transaction_value=transaction_value,
        transaction_date=transaction_date,
        account_type=account_type,
    )
    db.add(transaction)
    db.commit()
    transaction = (
        db.query(Transaction)
        .order_by(Transaction.transaction_id.desc())
        .filter(
            Transaction.transaction_name == transaction_name
            and Transaction.user_id == user_id,
        )
        .first()
    )
    return {"data": transaction}


# create a route to move funds from one account to another
@app.post("/move_funds", status_code=201)
def move_funds(
    user_id: int,
    transaction_value: float,
    transaction_date: str,
    account_type: str,
    db: Session = Depends(get_db),
):
    # check if user exists
    existing_user = (
        db.query(User)
        .filter(
            User.user_id == user_id,
        )
        .first()
    )
    if existing_user is None:
        return {"error": "There is no user with that id"}

    # defining the direction of the transaction
    if account_type == "main":
        account_debit = "savings"
        account_credit = "main"
    else:
        account_debit = "main"
        account_credit = "savings"

    # get the origin account balance
    main_account_credit = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.account_type == account_debit,
            Transaction.transaction_type == "credit",
        )
        .all()
    )
    # get the total credit amount of origin account
    main_account_credit_total = 0
    for transaction in main_account_credit:
        main_account_credit_total += transaction.transaction_value

    # get the origin account debits
    main_account_debit = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.account_type == account_debit,
            Transaction.transaction_type == "debit",
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
        return {"error": "Not enough funds to move funds"}

    # debit transaction
    debit_transaction = Transaction(
        user_id=user_id,
        transaction_name="Transfer funds",
        transaction_category="Transfer",
        transaction_type="debit",
        transaction_value=transaction_value,
        transaction_date=transaction_date,
        account_type=account_debit,
    )
    db.add(debit_transaction)
    db.commit()

    # credit transaction
    credit_transaction = Transaction(
        user_id=user_id,
        transaction_name="Receive funds",
        transaction_category="Transfer",
        transaction_type="credit",
        transaction_value=transaction_value,
        transaction_date=transaction_date,
        account_type=account_credit,
    )
    db.add(credit_transaction)
    db.commit()
    transaction_credit_registered = (
        db.query(Transaction)
        .order_by(Transaction.transaction_id.desc())
        .filter(
            Transaction.transaction_category == "Transfer"
            and Transaction.user_id == user_id,
        )
        .first()
    )
    return {
        "Message": "Funds moved successfully",
        "data": transaction_credit_registered,
    }


# create a route to return all suggestions
@app.get("/suggestions")
def read_suggestions(db: Session = Depends(get_db)):
    suggestions = db.query(Suggestion).all()
    return {"data": suggestions}


# create a route to add a suggestion
@app.post("/suggestions", status_code=201)
def create_suggestion(
    category: str,
    description: str,
    db: Session = Depends(get_db),
):
    suggestion = Suggestion(
        category=category,
        description=description,
    )
    db.add(suggestion)
    db.commit()
    suggestion = (
        db.query(Suggestion)
        .order_by(Suggestion.suggestion_id.desc())
        .filter(
            Suggestion.category == category,
        )
        .first()
    )
    return {"data": suggestion}
