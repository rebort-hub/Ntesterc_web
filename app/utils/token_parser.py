from jose import jwt
from app.settings.config import JWT_ALGORITHM, JWT_SECRET_KEY


class TokenParser:
    def analyze_token(self, token: str) -> dict:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
