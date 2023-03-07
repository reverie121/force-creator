import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

POSTGRES_DATABASE_PWD = os.environ.get("POSTGRES_DATABASE_PWD")
FC_DATABASE_URI = os.environ.get("FC_DATABASE_URL")
FC_SECRET_KEY = os.environ.get("FC_SECRET_KEY")