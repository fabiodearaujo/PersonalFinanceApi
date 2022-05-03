# necessary imports
from decouple import config
from fastapi import FastAPI, status
from httplib2 import Authentication

from .database import engine
from .models import Base
from .routers import auth, suggestions, transactions, users

# create the tables in the database
# if they are not already created
Base.metadata.create_all(bind=engine)

# App repository link setup
app_download = config("APP_URL")

# create a FastAPI app instance
app = FastAPI(
    title="Personal Finance API",
    description="This API is used to manage personal finance throught the APP.",
    version="0.1.0",
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(suggestions.router, prefix="/suggestions", tags=["suggestions"])
app.include_router(auth.router, prefix="/auth", tags=["authorization"])


# create the root route
@app.get("/")
def read_root():
    return {
        "Welcome to Personal Finance API": f"Get our app at {app_download}"
    }, status.HTTP_200_OK
