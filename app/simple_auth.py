# Simple authentication WITHOUT JWT - for local testing only
import hashlib
import secrets
from datetime import datetime, timedelta

# Simple token storage (in memory - for testing only)
tokens = {}

def create_token(data: dict):
    token = secrets.token_urlsafe(32)
    expiry = datetime.now() + timedelta(hours=8)
    tokens[token] = {"data": data, "expiry": expiry}
    return token

def decode_token(token: str):
    token_data = tokens.get(token)
    if token_data and token_data["expiry"] > datetime.now():
        return token_data["data"]
    return None
