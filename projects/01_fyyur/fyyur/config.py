import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL #entered 1/14
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:arthurcutillo@localhost:5432/myapp'
