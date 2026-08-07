#!/usr/bin/env python

# Database scripts

from sqlmodel import SQLModel, Field, Session, create_engine, select # DB


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