# necessary imports
import time

import psycopg2
from decouple import config
from fastapi import Depends, FastAPI
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

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


@app.get("/sqlalchemy/")
def get_sqlalchemy_get_users(db: Session = Depends(get_db)):
    """
    Get all users from the database
    """
    users = db.query(models.User).all()
    return {"data": users}


# create the root route
@app.get("/")
def read_root():
    return {"Welcome to Personal Finance API": "Get our app at APP_URL"}


# create a route to return one user
@app.get("/users/{email}")
def read_user(email: str):
    cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
    user = cursor.fetchone()
    return {"data": user}


# create a route to return all transactions from a user
@app.get("/users/transactions/{user_id}")
def read_transactions(user_id: int):
    cursor.execute(f"SELECT * FROM transactions WHERE user_id = {user_id}")
    transactions = cursor.fetchall()
    return {"data": transactions}


# create a route to return all suggestions
@app.get("/suggestions")
def read_suggestions():
    cursor.execute("SELECT * FROM suggestions")
    suggestions = cursor.fetchall()
    return {"data": suggestions}
