import os
from base64 import b64decode, b64encode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from typing import Literal

from maleo_core.utils.keyloader import load_rsa

class EncryptionService:
    #* Function to encrypt using RSA algorithm
    @staticmethod
    def encrypt_rsa(scope:Literal["backend", "frontend"], message:str) -> str:
        public_key = load_rsa(key_scope=scope, key_type='public') #* Load the public key
        cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256) #* Initialize cipher with OAEP padding and SHA-256
        encrypted_message = b64encode(cipher.encrypt(message.encode('utf-8'))).decode('utf-8') #* Encrypt the message and return as base64-encoded string
        return encrypted_message

    #* Function to decrypt using RSA algorithm
    @staticmethod
    def decrypt_rsa(message:str) -> str:
        private_key = load_rsa(key_scope='backend', key_type='private') #* Load the private key
        cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256) #* Initialize cipher with OAEP padding and SHA-256
        decrypted_message = cipher.decrypt(b64decode(message)) #* Decode the base64-encoded encrypted message and decrypt
        return decrypted_message.decode('utf-8')

    #* Function to encrypt using AES algorithm
    @staticmethod
    def encrypt_aes(message:str) -> tuple[str, str, str]:
        #* Define random AES key and initialization vector bytes
        aes_key_bytes = os.urandom(32)
        initialization_vector_bytes = os.urandom(16)
        #* Encrypt message with encryptor instance
        cipher = Cipher(algorithms.AES(aes_key_bytes), modes.CFB(initialization_vector_bytes), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_message = b64encode(encryptor.update(message.encode()) + encryptor.finalize()).decode('utf-8')
        #* Encode the results to base64 strings
        aes_key = b64encode(aes_key_bytes).decode('utf-8')
        initialization_vector = b64encode(initialization_vector_bytes).decode('utf-8')
        #* Return the AES key, IV, and encrypted messages
        return aes_key, initialization_vector, encrypted_message

    #* Function to decrypt using AES algorithm
    @staticmethod
    def decrypt_aes(aes_key:str, initialization_vector:str, message:str) -> str:
        #* Decode base64-encoded AES key, IV, and encrypted message
        aes_key_bytes = b64decode(aes_key)
        initialization_vector_bytes = b64decode(initialization_vector)
        #* Decrypt message with decryptor instance
        cipher = Cipher(algorithms.AES(aes_key_bytes), modes.CFB(initialization_vector_bytes), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_message = decryptor.update(b64decode(message)) + decryptor.finalize()
        #* Return the decrypted message
        return decrypted_message.decode("utf-8")