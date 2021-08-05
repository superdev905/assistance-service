from datetime import datetime
from jose import jwt
from passlib.context import CryptContext

from app.settings import SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return decoded_token if decoded_token["exp"] >= datetime.utcnow().timestamp() else None
    except Exception as e:
        print(e)
        return {}
