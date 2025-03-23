import jwt
from pydantic import ValidationError
from typing import Optional

from maleo_core.models import BaseTransfers
from maleo_core.utils.keyloader import load_rsa

class TokenService:
    @staticmethod
    def encode(payload:BaseTransfers.Payload.Token) -> str:
        payload_dict = payload.model_dump()
        payload_dict['uuid'] = str(payload_dict['uuid'])
        token = jwt.encode(
            payload=payload_dict,
            key=load_rsa(key_scope="backend", key_type="private").export_key(),
            algorithm="RS256"
        )
        return token

    @staticmethod
    def decode(token:str) -> Optional[BaseTransfers.Payload.Token]:
        try:
            payload = jwt.decode(token, key=load_rsa(key_scope="backend", key_type="public").export_key(), algorithms=["RS256"])
            payload = BaseTransfers.Payload.Token.model_validate(payload)
            return payload
        except jwt.PyJWTError as e:
            return None
        except ValidationError as e:
            return None