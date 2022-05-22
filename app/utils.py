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
    if len(password) < 8:
        return False
    elif len(password) > 20:
        return False
    elif password.isdigit():
        return False
    elif password.isalpha():
        return False
    else:
        return True


# function to get the current date
def get_current_date():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    return today