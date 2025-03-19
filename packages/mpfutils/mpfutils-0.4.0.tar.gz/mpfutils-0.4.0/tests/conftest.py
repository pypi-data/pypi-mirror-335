import logging
from dotenv import load_dotenv

# ignore logs from azure, openai and httpx
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv()