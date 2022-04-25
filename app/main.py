# necessary imports
import psycopg2
from decouple import config
from fastapi import FastAPI
from psycopg2.extras import RealDictCursor

# create a FastAPI app instance
app = FastAPI()


# configuring the environment variables
DB_NAME = config('DB_NAME')
DB_PASS = config('DB_PASS')

# database connection
try:
    conn = psycopg2.connect(host='localhost', database=DB_NAME, user='postgres', 
                            password=DB_PASS, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Connected to database")
except Exception as e:
    print("Unable to connect to database")
    print("Error: ", e)


# create the root route
@app.get("/")
def read_root():
    return {"Hello": "World"}

