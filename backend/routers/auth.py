#!/usr/bin/env python

# Authencation - e.g. login, register

import fastapi

# Sets the router for this script to /api/auth
router = fastapi.APIRouter(
    prefix="/auth", 
    tags=["Authentication"]
    )