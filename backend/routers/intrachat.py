#!/usr/bin/env python

# IntraChat App Router

import fastapi

# Sets the router for this script to /api/auth
router = fastapi.APIRouter(
    prefix="/intrachat", 
    tags=["IntraChat"]
)