import pyrogram
import os
import sys

print(f"Python Version: {sys.version}")
print(f"Pyrogram Version: {pyrogram.__version__}")
print(f"Pyrogram Path: {pyrogram.__file__}")

# Check if it's the fixed version
import inspect
from pyrogram.types import ChatPermissions
print(f"ChatPermissions init signature: {inspect.signature(ChatPermissions.__init__)}")

# Check system time
import time
import requests
try:
    r = requests.get("https://google.com", timeout=5)
    from email.utils import parsedate_to_datetime
    server_t = parsedate_to_datetime(r.headers['Date']).timestamp()
    print(f"Sync Check: Local={time.time()}, Server={server_t}, Delta={time.time() - server_t}")
except Exception as e:
    print(f"Sync check failed: {e}")
