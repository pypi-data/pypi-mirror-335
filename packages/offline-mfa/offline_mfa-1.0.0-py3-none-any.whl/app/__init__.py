# app/__init__.py

# Import key modules to make them accessible when importing 'app'
from .auth import *
from .main import *
from .user_store import *

# Package metadata
__version__ = "0.1.0"
__author__ = "Your Name"

# Any global initialization can go here
print("App package initialized.")
