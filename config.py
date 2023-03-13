import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

POSTGRES_MASTER_PWD = os.environ.get("POSTGRES_MASTER_PWD")
DATABASE_URI = os.environ.get("DATABASE_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")
IS_LOCAL = os.environ.get("IS_LOCAL", 0)