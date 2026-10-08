import os
from dotenv import load_dotenv

load_dotenv()

API_BASE: str = os.getenv("API_BASE", "https://api.openai.com/v1")
MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
API_KEY: str = os.getenv("API_KEY", "")
OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")
