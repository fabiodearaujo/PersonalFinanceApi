import re
import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# function to hash the password
def hash_context(password: str):
    return pwd_context.hash(password)


# function to verify the password
def verify_context(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# function to check password strength
def check_password_strength(password):
    if not re.search("[a-z]", password):
        return False
    elif not re.search("[A-Z]", password):
        return False
    elif not re.search("[$-/:-?{-~!^_`\[\]]", password):
        return False
    elif not re.search(r"\d", password):
        return False
    elif len(password) < 8:
        return False
    elif len(password) > 20:
        return False
    else:
        return True


# function to get the current date
def get_current_date():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    return today