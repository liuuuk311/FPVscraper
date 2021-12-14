import os
from urllib.parse import quote

import requests

API_KEY = os.environ.get("TELEGRAM_BOT_API_KEY")
API_URL = f"https://api.telegram.org/bot{API_KEY}/sendMessage?chat_id=38734421&text="


def telegram_log(message: str):
    requests.get(API_URL + quote(message))

