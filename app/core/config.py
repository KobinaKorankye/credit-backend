import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

class Settings:
    DB_URL: str = os.getenv("DB_URL")  # Replace process.env.DB_URL with os.getenv("DB_URL")

settings = Settings()
