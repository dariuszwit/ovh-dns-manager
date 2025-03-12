#!/usr/bin/env python
# passenger_wsgi.py
import sys
import os

# Add the project root directory to the system path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask application and expose it as 'application'
from app import app as application
