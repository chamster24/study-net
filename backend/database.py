#!/usr/bin/env python

# Database scripts

from sqlmodel import SQLModel, Field, Session, create_engine, select # DB
from datetime import datetime, timezone, timedelta
from pathlib import Path
from uuid import uuid4 # Needed to prevent naming conficts in db_users.uuid
import tomllib # Config file parsing
from sqlalchemy.exc import IntegrityError


import security as sec


# ----------
# Finds the version

version = ""
# 1. Find the absolute path to this script
script_dir = Path(__file__).resolve().parent
# 2. Go up one directory and points to the version file
target_file = script_dir.parent / "version.txt"

try:
    with open(target_file, "r") as file:
        version = file.read().strip()
except Exception:
    version = "*UNKNOWN"



# --------------------
# Logging
def log(message: str, level: int | None = None, perm: bool = False): #TODO: Rewrite to be better, e.g. make lvls 1/2 not appear unless DEBUG is set to true in toml
    log_file = script_dir.parent / "logs" / "database_log.txt"
    current_time_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    LEVEL_PREFIXES = {
        # Fine-grained / Verbose Diagnostic (0-2)
        0: "        | ",  # Plain continuation / indent
        1: "[TRACE] | ",  # Line-by-line execution details
        2: "[DEBUG] | ",  # Developer troubleshooting info
        # Operational (3-4)
        3: "[INFO]  | ",  # Standard operational status
        4: "[LOG]   | ",  # Generic log entry
        # Non-fatal warnings (5-6)
        5: "[NOTIC] | ",  # Significant event, not an error
        6: "[WARN]  | ",  # Something unexpected happened
        # Failures (7-9)
        7: "[ERROR] | ",  # Error
        8: "[CRIT]  | ",  # Critical error
        9: "[FATAL] | ",  # Fatal crash
        
        # Extras / Custom (10+)
        10: "[AUDIT] | ", # 
        11: "[PERF]  | ", # Performance
    }
    eval_level = LEVEL_PREFIXES.get(level, "        | " if perm else "")

    
    loggedmessage = eval_level + current_time_utc + " | " + message
    if perm:
        log_file.parent.mkdir(parents=True, exist_ok=True)  # Ensures the "logs" folder exists
        with open(log_file, "a") as file: # Auto closes it when done
            file.write(loggedmessage + "\n")
            print(f"LOGGED: \"{loggedmessage}\"")
    else:
        print(loggedmessage)
            

# --------------------
# Databases (sqlmodel classes)
class db_users(SQLModel, table=True): # User overview
    __tablename__ = "db_users"
    uuid: str = Field(primary_key=True, default_factory=lambda: str(uuid4())) # Dynamically generates the default uuid if one is not provided; lambda since brackets are not allowed
    usernum: int | None = Field(index=True, unique=True, default=None) # Incremental; will be populated by script later on
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str # Hashed!
    display_name: str | None = Field(default=None) # May beused later on, None means display name is the same as username
    creation_datetime: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    flags: str = Field(default="") # Status tags, such as ADMIN

class db_jwts(SQLModel, table=True):
    __tablename__ = "db_jwts"
    id: int | None = Field(default=None, primary_key=True) # Incremental; will be populated by SQL automatically
    uuid: str = Field(foreign_key="db_users.uuid", index=True)
    jti: str = Field(index=True, unique=True)
    # Will NOT store JWT

class db_userdata(SQLModel, table=True):
    __tablename__ = "db_userdata"
    id: int | None = Field(default=None, primary_key=True) # Incremental; will be populated by SQL automatically
    uuid: str = Field(foreign_key="db_users.uuid", index=True)
    encrypted_tf: bool
    data_type: str
    data: str



# --------------------
# Functions
# ----------
# Major Account Actions
# TODO: Fix so that instead of sending none, it just doesnt send that line. (? - is this still in effect? and if so, where?)

def adduser(data: dict): # TODO: Add try to outer, and integretyerror checks to see if the uuid, username, or email is duplicated - returning a diff num for each. However, the script that calls on this (will be routers/auth.py) should query the user (via database.py scripts) by uuid, username, and email first before the account gets added.
    with Session(engine) as session: # Auto opens and closes when the block is finished
        # 1. Create the object
        to_str = lambda val: str(val) if val is not None else None # Fixes "str(data.get("field", None))" errors
        def generate_uuid_if_missing(): # Added this to avoid errors for later on
            uuid = to_str(data.get("uuid"))
            if uuid != None:
                return uuid
            else:
                uuid = uuid4()
                data["uuid"] = uuid
                return uuid

        new_user = db_users(
            uuid = generate_uuid_if_missing(), # .get prevents TypeErrors to None if a uuid is somehow not provided
            usernum = None, # Since it's not the primary key, we have to manually populate it... LATER.
            username = str(data["username"]),
            email = str(data["email"]),
            password = str(data["password"]), # Hashed!
            display_name = str(data.get("display_name", data["username"])),
            creation_datetime = data.get("creation_datetime", None), # None, as the db will be able to make the datetime when it gets added to DB
            flags = to_str(data.get("flags"))
        )

        try:
            # 2. Stage to memory
            session.add(new_user)
            # 3. Save to disk
            session.commit()
            # 4. Fetch autogenerated fields
            session.refresh(new_user)
        except Exception: #TODO-SOMEDAY: Too lazy to check exception types
            log(f"SQLite: ABORTED - Exception (likely IntegrityError) while trying to add UUID {data["uuid"]}.")
            return 1


        # Finds the current largest usernum number, defaulting to 0 if no fields exist
        max_num = (
            session.exec(
                select(db_users.usernum).order_by(db_users.usernum.desc())
            ).first()
        ) or 0

        try: # 5. Set the UserNum #TODO
            getuserbyemail(data["email"])
            return 0
        except IntegrityError: # sqlalchemy.exc.IntegrityError
            log(f"SQLite: IntegrityError while trying to change usernum for UUID {data["uuid"]}",level=5 ,perm=False) # TODO, recheck maxnum and if maxnum is still the same try to add 1 until it works
            i = 0
            AddedtoDB = False
            while (i < 3):
                try:
                    max_num_prev = max_num
                    max_num = (
                        session.exec(
                            select(db_users.usernum).order_by(db_users.usernum.desc())
                        ).first()
                    ) or 0
                    if max_num_prev == max_num: # Try +i+1, since +1 didnt work
                        statement = select(db_users).where(db_users.uuid == data["uuid"])
                        result = session.exec(statement).first()
                        if result:
                            i += 1
                            setattr(result, "usernum", int(max_num + 1 + i))
                            session.commit()
                        else: # Should NOT happen
                            log(f"Account with UUID {data["uuid"]} was deleted between the time that it was created and the usernum was being assigned. This should NOT happen - please debug. (MaxNumPrev = MaxNum)", level=7, perm=True)
                            deleteuser(data["uuid"]) # Just in case
                            return 1
                        break # No errors, so it worked!

                    else: # Proceed by setting usernum by maxnum +1
                        i = 1 # First, reset i
                        statement = select(db_users).where(db_users.uuid == data["uuid"])
                        result = session.exec(statement).first()
                        if result:
                            i += 1
                            setattr(result, "usernum", int(max_num + 1))
                            session.commit()
                        else: # Should NOT happen
                            log(f"Account with uuid {data["uuid"]} was deleted between the time that it was created and the usernum was being assigned. This should NOT happen - please debug. (MaxNumPrev != MaxNum)", level=7, perm=True)
                            deleteuser(data["uuid"]) # Just in case
                            return 1 
                        break # No errors, so it worked!

                except Exception:
                    # It doesn't matter, try another time
                    i += 1

        except Exception: # Something went wrong
            log("Something wrong happened when adding a new user!", level=8, perm=True)
            deleteuser(data["uuid"]) # Just in case
            return 1 

        # Finally check usernum, return 1 and delete user if it fails



def deleteuser(uuid):
    with Session(engine) as session: 
        pass


# ----------
# Change User Data
# TODO: Optimize (via guard clauses) and make safer. Also, change input() to something like curses() so that uvicorn doesnt accidently freeze.
# IMPORTANT: for now, do NOT use terminal_override
def changeuseraccountinfo(subject_uuid, field, updvalue,initiating_jwt: str, admin_perms=False, terminal_override=False):
    pass
    """
    ALLOWED_USER_FIELDS = {"username", "display_name", "email"} # Safeguarding
    ALLOWED_ADMIN_FIELDS = ALLOWED_USER_FIELDS | {"uuid", "usernum", "password", "creation_datetime"}
    ALLOWED_TERMINAL_FIELDS = ALLOWED_ADMIN_FIELDS | {"flags"}
    if ((field in ALLOWED_USER_FIELDS) or (admin_perms) or terminal_override):
        if admin_perms and not terminal_override: # AdminMode
            jwtresult = checkjwt(initiating_jwt)
            if jwtresult["status"] != "valid": # AdminMode, Invalid JWT
                log(f"ABORTED - An admin tried changing Field \"{field}\" for UUID \"{subject_uuid}\", but had an invalid JWT.", level=5, perm=True)
                return 3
            else: # AdminMode, Valid JWT
                uuidresult = getuserbyuuid(jwtresult["jwtdata"]["sub"])
                if not (",admin," in uuidresult["flags"]): # AdminMode, Valid JWT, Invalid Adminship
                    log(f"ABORTED - An non-admin tried changing Field \"{field}\" for UUID \"{subject_uuid}\".", level=5, perm=True)
                    return 3
                else: # AdminMode, Valid JWT, Valid Adminship
                    pass # All OK!
        elif not terminal_override: # RegMode
            jwtresult = checkjwt(initiating_jwt, uuid=None, jti=None) # TODO: expects 3 arguements
            if jwtresult["status"] != "valid": # RegMode, Invalid JWT
                log(f"ABORTED - Someone tried changing Field \"{field}\" for UUID \"{subject_uuid}\", but had an invalid JWT.", level=5, perm=True)
                return 4
            else: # RegMode, Valid JWT
                if not (subject_uuid == jwtresult["jwtdata"]["sub"]): # RegMode, Valid JWT, Invalid User
                    log(f"ABORTED - A different user (\"{jwtresult['sub']}\") tried changing Field \"{field}\" for UUID \"{subject_uuid}\".", level=5, perm=True)
                    return 4
                else: # RegMode, Valid JWT, Valid User
                    pass # All OK!

        if not (field in ALLOWED_ADMIN_FIELDS): # Final check - is it allowed?
            if not terminal_override:
                log(f"ABORTED - UUID (\"{jwtresult["jwtdata"]["sub"]}\") tried changing Field \"{field}\" for UUID \"{subject_uuid}\", which was NOT permitted by ALLOWED_ADMIN_FIELDS and ", level=5, perm=True)
                return 5
            else:
                userinput = input(f"Are you sure you want to change Field \"{field}\" to \"{updvalue}\" for UUID \"{subject_uuid}\"?\nType \"Y\" + \"ENTER\" to CONFIRM - Anything else + \"ENTER\" to CANCEL")
                if userinput.lower() != "y":
                    log(f"Terminal ABORTED the change of field \"{field}\" for UUID \"{subject_uuid}\".", level=4, perm=True)
                    return 6
                else:  
                    if not (field in ALLOWED_TERMINAL_FIELDS):
                        userinput = input("Are you SURE you're SURE? This is NOT an AUTHORIZED_TERMINAL_FIELD value.\nType \"Y\" + \"ENTER\" to CONFIRM - Anything else + \"ENTER\" to CANCEL")
                        if userinput.lower() != "y":
                            log(f"Terminal ABORTED the change of field \"{field}\" for UUID \"{subject_uuid}\" (backup safety check).", level=4, perm=True)
                            return 6
                        else:
                            # They're SURE...
                            log(f"Terminal is preparing to change field \"{field}\" for UUID \"{subject_uuid}\".", level=4, perm=True)
                    else:
                        pass # All OK!

        with Session(engine) as session: # ! The actual db changes
            statement = select(db_users).where(db_users.uuid == subject_uuid)
            result = session.exec(statement).first()
            if result:
                setattr(result, field, updvalue)
                session.commit() # Saves to file

                if terminal_override:
                    log(f"Terminal changed field \"{field}\" for UUID \"{subject_uuid}\".", level=4, perm=True)
                if admin_perms:
                    log(f"Admin UUID \"{initiating_jwt}\" changed field \"{field}\" for UUID \"{subject_uuid}\".", level=4, perm=True)
                else:
                    log(f"UUID \"{subject_uuid}\" changed field \"{field}\".", level=4, perm=True)
                return 0
            
            else: # User does NOT exist in db
                if admin_perms:
                    log(f"ABORTED - Admin UUID \"{initiating_jwt}\" tried changing field \"{field}\" for a nonexistant UUID (\"{subject_uuid}\")", level=5, perm=True)
                else:
                    log(f"ABORTED - Someone tried changing field \"{field}\" for a nonexistant UUID (\"{subject_uuid}\")", level=7, perm=True) # This should NEVER happen given the previous RegMode checks, so something went wrong in the code.
                return 1
    else: # Not a default allowed field
        log(f"ABORTED - Someone tried changing field \"{field}\" without Admin perms!", level=5, perm=True)
        return 2
    """

def changeusersaveddata():
    with Session(engine) as session:
        pass


# ----------
# Query User
def getuserbyuuid(query_uuid):
    with Session(engine) as session:
        # 1. Build the statement
        statement = select(db_users).where(db_users.uuid == query_uuid) # Select() selects the table
        # 2. Run the statement and grab the result
        result = session.exec(statement).first() # Return ONE matching object or NONE
        # 3. Use the result
        if result:
            return result
        else:
            return None

def getuserbyusername(query_username):
    with Session(engine) as session:
        statement = select(db_users).where(db_users.username == query_username)
        result = session.exec(statement).first()
        if result:
            return result
        else:
            return None

def getuserbyemail(query_email): # Intended to be solely used by auth.py to check emails before they add it
    with Session(engine) as session:
        statement = select(db_users).where(db_users.email == query_email)
        result = session.exec(statement).first()
        if result:
            return result
        else:
            return None


# ----------
# Security Stuff
def addjwtid(jwtuuid): # This script is called by ? (TODO: Call from auth.py)
    with Session(engine) as session: # Checks for valid UUID
        statement = select(db_users).where(db_users.uuid == jwtuuid)
        result = session.exec(statement).first()
        if not result: # Inexistant UUID, should not happen
            log(f"ABORTED - Attempted to create a JWT for a nonexistant UUID (\"{jwtuuid}\").", level=5, perm=True)
            return 1
        result_dict = result.model_dump()
        generated_jwt = sec.generateJWT(jwtuuid, result_dict["username"]) # Generates the JWT
        # Add the JWT Token and JTI to db
        new_jwt = db_jwts(
            # ID will be autopopulated by SQL
            uuid = str(jwtuuid),
            jti = str(generated_jwt["jti"])
        )
        # Stage to memory
        session.add(new_jwt)
        # Save to file
        session.commit()
        # Fetch auto-generated fields
        session.refresh(new_jwt)
    return str(generated_jwt["jti"])


def revokejwtid():
    with Session(engine) as session:
        pass

def checkjwt(jwt: str, uuid: str | None):
    """
    UUID v7 is (not counting hyphens):
    Pos 1-12: millisecond UNIX timestamp (strip hyphen)
    Pos 13: Version flag (7)
    Pos 14-16: Sub-millisecond (although it COULD be calculated, we won't use it.)
    Pos 17: Varient flag
    Pos 18-36: Random
    """

    jwt_verification = sec.verifyJWT(jwt)
    # Guard Clause: checks status field of main dict
    if jwt_verification["status"] == False:
        # Determine the issue
        if jwt_verification["details"] == "expired": # Seems like nothing malicious. Return code 2, signaling INVALID but don't become overly protective
            return 2
        elif jwt_verification["details"] == "invalid": # Likely malicious. Informs the code (if it doesn't check for != 0 and instead for individual error number) to become more protective, just in case.
            return 1
        else:
            return 1 # Just in case!

    # Now, we check specific fields of the JWT.
    try:
        if not (jwt_verification["data"]["iss"] == "StudyNet"):
            return 1
        if not (jwt_verification["data"]["version"] == str(version)):
            return 2
        if uuid:
            if not (jwt_verification["data"]["sub"] == uuid):
                return 1
        # Username wont be checked, as UUID covers it
        # EXP/IAT also won't be checked, as the JWT decoder automatically checks it

        # Finally, check if the JTI is in DB
        if (jwt_verification["data"]["jti"]):
            with Session(engine) as session:
                statement = select(db_jwts).where(db_jwts.jti == jwt_verification["data"]["jti"]) 
                result = session.exec(statement).first()
                if not result:
                    return 2 # The user may have just revoked the JTI     
        else:
            return 1

        # If no errors trigger, we can return that the JWT is indeed valid.
        return 0
    except Exception: # Should not happen - catch-all
        return 1
        

def changeuserpassword(): # Although changeuseraccountinfo() could handle this, it is better to keep sensitive info seperate
    with Session(engine) as session:
        pass


# ----------
# Startup stuff

# There are two ways to config the sqlite url: a settings.toml file, or a database.db file in root.

# 1. Find the absolute path to this script
script_dir = Path(__file__).resolve().parent
# Go up one directory and points to the settings file
config_file = script_dir.parent / "config.toml"

# 2. First, try checking for the settings.toml file - If any part of this script fails, it runs the except block which sets the DB file path to root.
database_file = ""
# SQLite connection string
sqlite_url = ""
try:
    with open(config_file, "rb") as file: # Possible exception, if file is missing (supposed to be in root)
        # Parse file into a Python dict
        config = tomllib.load(file)

        # Pull the key value
        CFG_sqlite_url = config.get("database", {}).get("sqlite_url")
        if CFG_sqlite_url and CFG_sqlite_url != "`default`":
            sqlite_url = CFG_sqlite_url.replace("`script_dir.parent`", str(script_dir.parent)) # Replace any relative paths with actual path. Also, note that the file NEEDS to have the url prefix e.g. "sqlite://"
        else:
            raise ValueError("Defaulting to the default db path") # Possible exception - either the line doesnt exist, or the line is "`default`"
        
except Exception as e: # Something went wrong, sets database_file to default
    # Checks the exception type. Note that tomllib.TOMLDecodeError is before ValueError since tomllib inherits the error from ValueError
    if isinstance(e, tomllib.TOMLDecodeError):
        log("CONFIG: Decode error - config.toml contains invalid TOML.", level=7, perm=True)
    elif isinstance(e, ValueError):
        log("CONFIG, SQLITE: Defaulting to the default db path, since \"`default`\" was provided in config field \"sqlite_url\".", level=5, perm=False)
    elif isinstance(e, FileNotFoundError):
        log("CONFIG: Settings file doesn't exist - defaulting to the default db path.", level=6, perm=False)
    elif isinstance(e, PermissionError):
        log("CONFIG: Permission error - can not access config file.", level=7, perm=True)
    else:
        log(f"CONFIG: Other Error: \"{e}\"", level=7, perm=True)
    
    # Go up one directory and points to the database file
    database_file = script_dir.parent / "database.db"
    sqlite_url = f"sqlite:///{database_file}"




# Create the SQLModel engine
engine = create_engine(sqlite_url, echo=False)


def init_db():
	# Creates the DB file and all missing tables
	SQLModel.metadata.create_all(engine)

# Removed Database Creation Script for the default SQLModel db creation script
"""
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
"""