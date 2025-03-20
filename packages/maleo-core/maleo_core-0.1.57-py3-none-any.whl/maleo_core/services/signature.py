from base64 import b64decode, b64encode
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

from maleo_core.utils.keyloader import load_rsa

class SignatureService:
    #* Function to create signature
    @staticmethod
    def sign(message:str) -> str:
        private_key = load_rsa(key_scope='backend', key_type='private')

        # Create SHA256 hash of the message
        message_hash = SHA256.new(message.encode('utf-8'))

        # Sign the hashed message
        signature = pkcs1_15.new(private_key).sign(message_hash)
        return b64encode(signature).decode('utf-8')

    #* Function to verify signature
    @staticmethod
    def verify(scope:str, message:str,signature: str) -> bool:
        public_key = load_rsa(key_scope=scope, key_type='public')

        # Create SHA256 hash of the message
        message_hash = SHA256.new(message.encode('utf-8'))

        try:
            # Verify the hashed message and decoded signature
            pkcs1_15.new(public_key).verify(message_hash, b64decode(signature))
            return True
        except (ValueError, TypeError):
            return False