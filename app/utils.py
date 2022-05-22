import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_context(password: str):
    return pwd_context.hash(password)


def verify_context(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_current_date():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    return today