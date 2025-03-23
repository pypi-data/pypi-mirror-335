import socket
import os

from dotenv import load_dotenv

load_dotenv()

backend_override = os.environ.get("BACKEND_OVERRIDE")
# If backend_override is local host, use the socket.gethostname() to get the local host name
if "localhost" in backend_override:
    port = backend_override.split(":")[-1].split("/")[0]
    backend_override = f"http://{socket.gethostname()}.local:{port}/api"

LE_APIM = f"https://liquidearthapim-prod001.azure-api.net/python/"
BASE_URL = LE_APIM if backend_override is None else backend_override
