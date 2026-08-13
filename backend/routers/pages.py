#!/usr/bin/env python

# Distribution of dynamic webpages

import fastapi
import jinja2

# Sets the router for this script to /api/pages
router = fastapi.APIRouter(
    prefix="/pages", 
    tags=["Pages"]
)