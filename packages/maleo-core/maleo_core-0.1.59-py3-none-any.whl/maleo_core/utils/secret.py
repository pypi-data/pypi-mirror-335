from google.cloud import secretmanager
from google.oauth2 import service_account
from google.auth import default
from google.api_core import retry
from typing import Optional
import os

class SecretManagerClient:
    def __init__(
        self,
        project_id:Optional[str] = None,
        credentials_path:Optional[str] = None,
        credentials_dict:Optional[dict] = None,
        use_default_credentials:bool = True
    ):
        """
        Initialize the Secret Manager client.
        
        Args:
            project_id: Google Cloud project ID. If None, reads from GCP_PROJECT_ID env var
            credentials_path: Path to service account JSON file
            credentials_dict: Dictionary containing service account info
            use_default_credentials: Whether to fall back to application default credentials
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        if not self.project_id:
            raise ValueError("Project ID must be provided or set in GCP_PROJECT_ID environment variable")

        # Setup credentials with fallback chain
        credentials = None
        try:
            if credentials_dict:
                credentials = service_account.Credentials.from_service_account_info(credentials_dict)
            elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                credentials = service_account.Credentials.from_service_account_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
            elif credentials_path:
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
            elif use_default_credentials:
                credentials, project = default()
        except Exception as e:
            if not use_default_credentials:
                raise ValueError(f"Failed to initialize credentials: {str(e)}")
            # If use_default_credentials is True, we'll let the client handle it

        self.client = secretmanager.SecretManagerServiceClient(credentials=credentials)

    @retry.Retry(predicate=retry.if_exception_type(Exception), timeout=5)
    def get_secret(self, secret_name:str, version:str = "latest") -> bytes:
        """
        Fetch a secret from Secret Manager with retry logic.
        
        Args:
            secret_name: Name of the secret
            version: Version of the secret (default: "latest")
            
        Returns:
            Secret value as bytes
            
        Raises:
            ValueError: If project_id is not set
            PermissionDenied: If service account lacks necessary permissions
            NotFound: If secret doesn't exist
        """
        try:
            secret_path = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
            response = self.client.access_secret_version(name=secret_path)
            return response.payload.data
        except Exception as e:
            print(f"Error accessing secret {secret_name}: {str(e)}")
            raise

    def get_secret_string(self, secret_name:str, version:str = "latest") -> str:
        """Get secret as a UTF-8 string."""
        return self.get_secret(secret_name, version).decode('utf-8')