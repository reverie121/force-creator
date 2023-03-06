import os

class Config(object):
    POSTGRES_DATABASE_PWD = os.environ.get("POSTGRES_DATABASE_PWD")
    FC_DATABASE_URI = os.environ.get("FC_DATABASE_URL")
    FC_SECRET_KEY = os.environ.get("FC_SECRET_KEY")