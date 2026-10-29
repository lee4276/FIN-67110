import os

from desk import ROOT, load_env


load_env(ROOT / ".env")

api_key = os.getenv("API_KEY", "")
print(f"{api_key[:4]}...")
print(os.getenv("SEC_USER_AGENT", ""))
