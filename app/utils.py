import datetime
import re

import bcrypt


# function to hash the password
def hash_context(password: str):
    # Truncate password to 72 bytes if necessary
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return bytes(hashed).hex()


# function to verify the password
def verify_context(plain_password, hashed_password):
    try:
        # Truncate password to 72 bytes if necessary
        password_bytes = plain_password.encode("utf-8")[:72]
        if isinstance(hashed_password, str):
            # Remove '\\x' sequences if present and convert hex string back to bytes
            cleaned_hash = hashed_password.replace("\\x", "")
            hashed_bytes = bytes.fromhex(cleaned_hash)
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        return bcrypt.checkpw(password_bytes, hashed_password)
    except Exception as e:
        print(f"Error verifying password: {e}")
        print(f"Password bytes: {password_bytes}")
        print(f"Hashed password: {hashed_password}")
        return False


# function to check password strength
def check_password_strength(password):
    # Minimum 8 characters, maximum 20 characters, at least one uppercase letter, one lowercase letter, one number and one special character
    pattern = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$"
    )
    return bool(pattern.match(password))

# function to get the current date
def get_current_date():
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    return today
