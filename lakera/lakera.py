import os
import requests
from utils.logger_setup import getlogger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = getlogger("lakera")

API_KEY = os.getenv("LAKERA_API_KEY")
if not API_KEY:
    logger.error("Missing LAKERA_API_KEY environment")

API_URL = "https://api.lakera.ai/v2/guard"

def screen_with_lakera(input_text, output_text=None):
    messages = [{"role": "user", "content": str(input_text)}]
    if output_text is not None:
        messages.append({"role": "assistant", "content": str(output_text)})

    payload = {
        "messages": messages,
        "project_id": os.getenv("LAKERA_PROJECT_ID")
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    logger.info(f"Lakera request payload: {payload}")
    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    logger.info(f"Lakera response: {result}")
    return result
