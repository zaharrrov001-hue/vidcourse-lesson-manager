"""Configuration management for VidCourse Lesson Manager."""
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    """Application configuration."""
    
    # Google Drive settings
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_TOKEN_FILE: str = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
    
    # GetCourse API settings
    GETCOURSE_API_KEY: Optional[str] = os.getenv("GETCOURSE_API_KEY")
    GETCOURSE_API_URL: str = os.getenv("GETCOURSE_API_URL", "https://api.getcourse.ru")
    GETCOURSE_ACCOUNT: Optional[str] = os.getenv("GETCOURSE_ACCOUNT")
    
    # Google Drive API scopes
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        required = [
            cls.GOOGLE_DRIVE_FOLDER_ID,
            cls.GETCOURSE_API_KEY,
            cls.GETCOURSE_ACCOUNT,
        ]
        return all(required)
    
    @classmethod
    def get_missing_config(cls) -> list:
        """Get list of missing configuration items."""
        missing = []
        if not cls.GOOGLE_DRIVE_FOLDER_ID:
            missing.append("GOOGLE_DRIVE_FOLDER_ID")
        if not cls.GETCOURSE_API_KEY:
            missing.append("GETCOURSE_API_KEY")
        if not cls.GETCOURSE_ACCOUNT:
            missing.append("GETCOURSE_ACCOUNT")
        return missing