import jwt
import os
import bcrypt
from datetime import datetime, timezone, timedelta

 
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440")) 

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    
    Args:   
        password (str): The plain-text password to hash.
        
    Returns:
        str: The hashed password.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against the hashed one.
    
    Args:
        plain_password (str): The plain password to verify.
        hashed_password (str): The hashed password stored in DB.
        
    Returns:
        bool: True if matched, else False.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))




def create_access_token(data: dict) -> str:
    """
    Creates a JWT token with expiry using PyJWT.
    """
    # 24 hours
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodes and verifies a JWT token.
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

