import os
from pathlib import Path
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class ContactsConfig(BaseModel):
    """Configuration for Google Contacts integration."""
    google_client_id: Optional[str] = Field(
        default=None,
        description="Google OAuth client ID"
    )
    google_client_secret: Optional[str] = Field(
        default=None,
        description="Google OAuth client secret"
    )
    google_refresh_token: Optional[str] = Field(
        default=None,
        description="Google OAuth refresh token"
    )
    credentials_paths: List[Path] = Field(
        default_factory=list,
        description="Paths to search for credentials.json file"
    )
    token_path: Path = Field(
        default=Path.home() / ".config" / "google-contacts-mcp" / "token.json",
        description="Path to store the token file"
    )
    default_max_results: int = Field(
        default=100,
        description="Default maximum number of results to return"
    )
    scopes: List[str] = Field(
        default=[
            'https://www.googleapis.com/auth/contacts',
            'https://www.googleapis.com/auth/directory.readonly'
        ],
        description="OAuth scopes required for the application"
    )

def load_config() -> ContactsConfig:
    """Load configuration from environment variables and defaults."""
    # Default credentials paths to check
    default_paths = [
        Path.home() / ".config" / "google" / "credentials.json",
        Path.home() / "google_credentials.json",
        Path(__file__).parent / "credentials.json"
    ]
    
    # Create token directory if it doesn't exist
    token_dir = Path.home() / ".config" / "google-contacts-mcp"
    token_dir.mkdir(parents=True, exist_ok=True)
    
    return ContactsConfig(
        google_client_id=os.environ.get("GOOGLE_CLIENT_ID"),
        google_client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
        google_refresh_token=os.environ.get("GOOGLE_REFRESH_TOKEN"),
        credentials_paths=default_paths,
        token_path=token_dir / "token.json"
    )

# Global configuration instance
config = load_config()
