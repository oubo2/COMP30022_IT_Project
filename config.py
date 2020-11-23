import os
from dotenv import load_dotenv

# Reads the local .env file
load_dotenv()

# S3 Credentials
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_KEY = os.environ.get("S3_KEY")
S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY")

# Flask secret key for sessions and cookies
SECRET_KEY = os.environ.get("SECRET_KEY")
