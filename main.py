from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from database import connect_to_mongodb, close_mongodb_connection, database
from Routes import events, attendees
from Utils.helpers import create_access_token, verify_password, get_current_user
from models import Token, User
from config import settings


app = FastAPI(title="Event Management API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database connection events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongodb()


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongodb_connection()


# Include routers
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(attendees.router, prefix="/attendees", tags=["attendees"])


# Root endpoint

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Use the database object imported from database.py
    user = await database.users.find_one({"username": form_data.username})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user