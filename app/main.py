# necessary imports
from decouple import config
from fastapi import FastAPI, status

from .models import Base
from .database import engine
from .routers import users, transactions, suggestions

# create the tables in the database 
# if they are not already created
Base.metadata.create_all(bind=engine)

# App repository link setup
app_download = config("APP_URL")

# create a FastAPI app instance
app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(suggestions.router, prefix="/suggestions", tags=["suggestions"])

# create the root route
@app.get("/")
def read_root():
    return {f"Welcome to Personal Finance API": "Get our app at {app_download}"}, status.HTTP_200_OK
