#!/usr/bin/env python

import fastapi # Web framework
import uvicorn # Web server
from argon2 import PasswordHasher
import jwt # Specifically PyJWT, not JWT; Generates JSON Web Tokens (session keys)
import uuid # UUID
import secrets # Base keys for JWT to generate JSON Web Tokens
from sqlmodel import SQLModel, Field, Session, create_engine, select # DB
from datetime import datetime, timezone, timedelta # JWT Session Key expiry

from routers import auth, intrachat # Imports all FastAPI router scripts
import database as db
import security as sc

# Sets up FastAPI
app = fastapi.FastAPI()

# Sets up the default top-level prefix as /api
api_router = fastapi.APIRouter(prefix="/api")

# Scripts to connect with routers
api_router.include_router(auth.router) # This needs to be repeated for each router (TODO)
app.include_router(api_router)

@app.get("/")
def returnresponse():
    return {"status": "online", "message": "approved"}

if __name__ == "__main__": # If this app is directly called on instead of imported, which is the default for this backend
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True) # Runs app.py as var app on http://127.0.0.1