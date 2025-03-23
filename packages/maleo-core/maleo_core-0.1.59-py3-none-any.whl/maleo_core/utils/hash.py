from passlib.context import CryptContext
from passlib.exc import UnknownHashError

CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

class HashLib:
    @staticmethod
    def hash(password:str) -> str:
        return CONTEXT.hash(password)

    @staticmethod
    def validate(plain_password:str, hashed_password:str) -> bool:
        try:
            return CONTEXT.verify(plain_password, hashed_password)
        except UnknownHashError:
            print("Invalid Hash")
            return False
        except Exception as e:
            print(f"An error occurred during hash verification: {e}")
            return False