# from datetime import datetime, timedelta
# from typing import Optional
# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
#
# from models import TokenData, User
# from config import settings

# # Password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# # OAuth2 setup
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
#
# # JWT functions
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#
#     return encoded_jwt
#
#
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#
#     # In a real application, you would fetch the user from the database
#     # Here, we're just returning a mock user for simplicity
#     user = User(
#         username=token_data.username,
#         email=f"{token_data.username}@example.com",
#         full_name="Test User",
#         disabled=False
#     )
#
#     if user is None:
#         raise credentials_exception
#
#     return user
#
#
# def get_password_hash(password: str):
#     return pwd_context.hash(password)
#
#
# def verify_password(plain_password: str, hashed_password: str):
#     return pwd_context.verify(plain_password, hashed_password)

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from database import database # Import database object
from models import TokenData, User
from config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# JWT functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    print(f"Searching for user: {token_data.username}")

    # Fetch user from the database asynchronously
    user = await database.Users.find_one({"username": {"$regex": f"^{token_data.username}$", "$options": "i"}})
    print(f"User found: {user}")


    if user is None:
        raise credentials_exception

    # Adapt to match your user model.  Return the user dict directly, or create a User object.
    # For this example, I'm assuming your database user document has 'username', 'email', 'full_name', and 'disabled' fields.
    return User(
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        disabled=user["disabled"]
    )


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

