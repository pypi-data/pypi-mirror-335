from Crypto.PublicKey import RSA
from typing import Literal, Optional
from .secret import SecretManagerClient

#* Function to load RSA key from Google Secret Manager
def load_rsa(key_scope: Literal["backend", "frontend"], key_type: Literal["private", "public"]) -> Optional[RSA.RsaKey]:
    """
    Load an RSA key from Google Secret Manager.
    
    :param key_scope: Either "backend" or "frontend".
    :param key_type: Either "private" or "public".
    :return: RSA key object if found, else raises an error.
    """
    #* Define secret name based on scope and type
    secret_name = None
    if key_scope == "backend":
        secret_name = "maleo-be-private-key" if key_type == "private" else "maleo-be-public-key"
    elif key_scope == "frontend" and key_type == "public":
        secret_name = "maleo-fe-public-key"

    if not secret_name:
        raise ValueError("Invalid key scope or key type.")

    #* Fetch key from Google Secret Manager
    client = SecretManagerClient()
    key_data = client.get_secret(secret_name)
    if not key_data:
        raise FileNotFoundError(f"Key not found in Google Secret Manager: {secret_name}")

    #* Load RSA key using PyCryptodome's RSA.import_key
    rsa_key = RSA.import_key(key_data)

    #* Validate the key type
    if (key_type == "private" and rsa_key.has_private()) or (key_type == "public" and not rsa_key.has_private()):
        return rsa_key
    else:
        raise ValueError(f"The key from secret '{secret_name}' does not match the requested type '{key_type}'")
