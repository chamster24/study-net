#!/usr/bin/env python

# Database scripts

from sqlmodel import SQLModel, Field, Session, create_engine, select # DB
from datetime import datetime, timezone, timedelta
from pathlib import Path
import uuid

# TODO: Initialize SQLModel



# --------------------
# Databases (sqlmodel classes)
class db_Users(SQLModel, table=True): # User overview
    uuid: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4)) # Dynamically generates the default uuid if one is not provided, lambda since brackets are not allowed
    usernum: int | None = Field(index=True, unique=True) # Incremental; will be populated by script later on
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    display_name: str | None = Field(default=None) # May be used later on, None means display name is the same as username
    creationdate: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class db_JWTs(SQLModel, table=True):
    id: int | None = Field(primary_key=True) # Incremental; will be populated by script later on
    # TODO

class db_UserData(SQLModel, table=True):
    pass



# --------------------
# Functions
# ----------
# Major Account Actions
def adduser():
    """
    The following fields are NEEDED:
    - User Number (e.g. #12345678, incremental, not needed now but may be useful in the future)
    - UUID (uuid v4)
    - Username
    - Email
    - Password 
    - Data (blank)
    - Active JWTs (blank, but as soon as the user is created the system should create a web token for the user client)
    - Created At (timestamp)
    -----
    The following fields are under consideration:
    - Account Status Fields (e.g. isadmin, isnotdisabled, etc)

    
    Also, many fields need to be encrypted/hashed (pswd).
    """
    pass

def deleteuser():
    pass


# ----------
# Change User Data
def changeuseraccountinfo():
    pass

def changeusersaveddata():
    pass


# ----------
# Query User
def getuserbyuuid(search_uuid):
    pass

def getuserbyusername(search_username):
    pass


# ----------
# Security Stuff
def addjwtid():
    pass

def revokejwtid():
    pass

def checkjti():
    pass

def changeuserpassword(): # Although changeuseraccountinfo() could handle this, it is better to keep sensitive info seperate
    pass


# ----------
# Startup stuff


# 1. Find the absolute path to this script
script_dir = Path(__file__).resolve().parent
# 2. Go up one directory and points to the database file
database_file = script_dir.parent / "database.db"

# Database creation script (should only EVER run once!)
def createdatabase():
    try:
        with open(database_file, "x") as f: # Creates the file and instantly closes it. "X" allows for error logging.
            pass
        print("File created successfully!")
        return 1 # Database CREATED
    except FileExistsError: # Should NOT happen
        print("\033[1;33m[WARNING]\033[0m createdatabase() tried to create database.db, but faced FileExistsError. There may be something wrong with startup(), or database.db was added into root between the time of the check and attempted file creation.") # \033[1;33m sets it to bolded yellow, and \033[0m resets the colors
    except PermissionError:
        print("\033[1;31m[FATAL]\033[0m Does not have permission to create the file.") # \033[1;31m sets it to bolded red, and \033[0m resets the colors
        raise # Errors out

# Startup file check
def startup(ranfromapp):
    if database_file.is_file(): # Checks if the file exists
        return 0 # Database EXISTS
    else:
        if ranfromapp == True: # Since app.py calls on it, we can safely run createdatabase and return its results
            return createdatabase()
        else: # Createdatabase() called this script, and the file creation failed - quits the program to prevent recusive loops
            print("\033[1;31m[FATAL]\033[0m createdatabase() tried to create the database and suceeded, but the file was moved or deleted between the time of creation and checking.") # \033[1;31m sets it to bolded red, and \033[0m resets the colors
            raise FileNotFoundError
            return 2 # Unused status code (failure)
            