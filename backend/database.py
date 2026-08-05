#!/usr/bin/env python

# Database scripts

from sqlmodel import SQLModel, Field, Session, create_engine, select # DB


# ----------
# Major Account Actions
def adduser():
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