from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def validate_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)