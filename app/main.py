# necessary imports
import psycopg2
import time
from decouple import config
from fastapi import FastAPI
from psycopg2.extras import RealDictCursor

# create a FastAPI app instance
app = FastAPI()


# configuring the environment variables
DB_USER = config('DB_USER')
DB_NAME = config('DB_NAME')
DB_ADDRESS = config('DB_ADDRESS')
DB_PASSWORD = config('DB_PASSWORD')

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
    return {"Hello": "World"}
