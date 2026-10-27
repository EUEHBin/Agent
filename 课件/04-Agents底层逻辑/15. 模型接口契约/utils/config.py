from dotenv import load_dotenv
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
_env_file = os.path.abspath(os.path.join(_current_dir, "../.env"))

load_dotenv(_env_file)

OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY")  # type: ignore
OPENAI_BASE_URL: str = os.environ.get("OPENAI_BASE_URL")  # type: ignore
OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL")  # type: ignore
