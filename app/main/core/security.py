import re
import string
import random
import jwt
import bcrypt
from datetime import timedelta, datetime
from random import randint, choice
from typing import Union, Any
from fastapi import HTTPException, status
from .config import Config
from app.main.core.i18n import __
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from string import ascii_lowercase, ascii_uppercase, digits, punctuation


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ALGORITHM = "HS256"


def validate_email(email):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return email_regex.match(email)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_code(length=6, end=True):
    """Generate a random string of fixed length """
    string_length = round(length / 2)
    letters = string.ascii_lowercase
    random_string = (''.join(choice(letters) for i in range(string_length))).upper()
    range_start = 10 ** ((length - string_length) - 1)
    range_end = (10 ** (length - string_length)) - 1
    random_number = randint(range_start, range_end)
    if not end:
        final_string = f"{random_string}{random_number}"
    else:
        final_string = f"{random_number}{random_string}"

    return final_string


def create_access_token(
        subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, Config.SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except Exception as e:
        if token:
            print("Failed to decode token")
            print(token)
            print(e)
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))



def check_pass(password: str):
    # 8 characters length and 1 special character
    pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
    result = re.findall(pattern, password)
    if (len(password) < 8) or not result:
        print("False")
        return False
    else:
        print("True")
        return True

def generate_password(min_length=12, max_length=16):
    """
    Generates a random password with at least min_length characters, containing at least:
    - 1 capital letter
    - 1 number
    - 1 special character
    """
    if min_length > max_length:
        tmp = max_length
        max_length = min_length
        min_length = tmp
    if min_length < 8: min_length = 8
    if max_length > 16: max_length = 16

    print(f"min: {min_length}")
    print(f"max: {max_length}")
    lowercase_letters = ascii_lowercase
    uppercase_letters = ascii_uppercase
    numbers = digits
    special_characters = punctuation

    # Ensure at least one character from each category
    guaranteed_chars = random.sample(lowercase_letters, 1)  # Lowercase
    guaranteed_chars.extend(random.sample(uppercase_letters, 1))  # Uppercase
    guaranteed_chars.extend(random.sample(numbers, 1))  # Number
    guaranteed_chars.extend(random.sample(special_characters, 1))  # Special

    # Choose a random length between min_length and max_length (inclusive)
    password_length = random.randint(min_length, max_length)

    # Fill remaining characters with any combination
    remaining_chars = random.sample(lowercase_letters + uppercase_letters + numbers + special_characters, password_length - 4)

    # Combine all characters and shuffle for randomness
    password = guaranteed_chars + remaining_chars
    random.shuffle(password)

    # Return the password as a string
    return ''.join(password)


def is_valid_password(password):
  """
  Checks if a password string meets the following requirements:
    - At least 8 characters long
    - Contains at least one lowercase letter
    - Contains at least one uppercase letter
    - Contains at least one number
    # - Contains at least one special character
  """
  min_length = 8
  lowercase = any(char in ascii_lowercase for char in password)
  uppercase = any(char in ascii_uppercase for char in password)
  number = any(char in digits for char in password)
  # special = any(char in punctuation for char in password)

  return (len(password) >= min_length and
          lowercase and uppercase and number)


def generate_matricule(length=12):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))