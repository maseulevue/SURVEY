from fastapi import FastAPI, HTTPException
from sqlmodel import Session , select
from contextlib import asynccontextmanager
from database import create_db_and_tables, engine
from fastapi.middleware.cors import CORSMiddleware

import hashlib
import hmac
import os

from models import survey, account, register, login

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",  # React development server
    "https://example.com",    # Production frontend
    "*"
] # Define allowed origins (domains that can access your API)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Allow these origins
    allow_credentials=True,       # Allow cookies, authentication headers
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)

def hash_password(password, salt=None):
    # new password: make a random salt. Checking a password: reuse the saved salt
    if salt is None:
        salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000)
    return salt.hex() + "$" + hashed.hex()

def check_password(password, saved_hash):
    salt = bytes.fromhex(saved_hash.split("$")[0])
    return hmac.compare_digest(hash_password(password, salt), saved_hash)

@app.get("/")
async def root():
    return {"message": "Hello Alexander Hamilton"}

@app.get("/Survey/{id}")
async def read_survey(id: int):
    with Session(engine) as session:
        print(id,'--------------------------------------------------------------')
        user = session.get(survey, id)
        if user is None:
            raise HTTPException(status_code=404, detail="Survey not found")
        return {"message": user}
    
@app.post("/Survey")
async def create_survey(survey  : survey):
    with Session(engine) as session:
        session.add(survey)
        session.commit()
        session.refresh(survey)
        return {"status": "success", "message": survey}

@app.post("/Register")
async def register_user(data : register):
    username = data.username.strip()
    if username == "" or len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Username is required and password must be at least 8 characters")
    if data.password != data.confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    with Session(engine) as session:
        statement = select(account).where(account.username == username)
        if session.exec(statement).first() is not None:
            raise HTTPException(status_code=400, detail="Username is already taken")
        new_account = account(username=username, password_hash=hash_password(data.password))
        session.add(new_account)
        session.commit()
        return {"status": "success", "message": "Account created"}

@app.post("/Login")
async def login_user(data : login):
    with Session(engine) as session:
        statement = select(account).where(account.username == data.username.strip())
        found = session.exec(statement).first()
        if found is None or not check_password(data.password, found.password_hash):
            raise HTTPException(status_code=401, detail="Wrong username or password")
        return {"status": "success", "message": "Login successful"}
