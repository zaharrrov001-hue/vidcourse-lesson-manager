"""Google Drive integration for fetching lessons."""
import os
import pickle
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import Config


class GoogleDriveClient:
    """Client for interacting with Google Drive API."""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API."""
        creds = None
        
        # Load existing token
        if os.path.exists(Config.GOOGLE_TOKEN_FILE):
            with open(Config.GOOGLE_TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Credentials file not found: {Config.GOOGLE_CREDENTIALS_FILE}\n"
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GOOGLE_CREDENTIALS_FILE, Config.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(Config.GOOGLE_TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        self.credentials = creds
        self.service = build('drive', 'v3', credentials=creds)
    
    def list_files_in_folder(self, folder_id: Optional[str] = None) -> List[Dict]:
        """
        List all files in a Google Drive folder.
        
        Args:
            folder_id: Google Drive folder ID. Uses config default if None.
        
        Returns:
            List of file metadata dictionaries.
        """
        folder_id = folder_id or Config.GOOGLE_DRIVE_FOLDER_ID
        if not folder_id:
            raise ValueError("Folder ID is required")
        
        try:
            files = []
            page_token = None
            
            while True:
                query = f"'{folder_id}' in parents and trashed=false"
                results = self.service.files().list(
                    q=query,
                    pageSize=100,
                    fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink)",
                    pageToken=page_token
                ).execute()
                
                files.extend(results.get('files', []))
                page_token = results.get('nextPageToken')
                
                if not page_token:
                    break
            
            return files
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise
    
    def get_file_content(self, file_id: str) -> bytes:
        """
        Download file content from Google Drive.
        
        Args:
            file_id: Google Drive file ID.
        
        Returns:
            File content as bytes.
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            content = request.execute()
            return content
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise
    
    def get_file_metadata(self, file_id: str) -> Dict:
        """
        Get file metadata.
        
        Args:
            file_id: Google Drive file ID.
        
        Returns:
            File metadata dictionary.
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, modifiedTime, webViewLink, description"
            ).execute()
            return file
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise
    
    def export_file(self, file_id: str, mime_type: str) -> bytes:
        """
        Export Google Workspace file (Docs, Sheets, Slides) to specified format.
        
        Args:
            file_id: Google Drive file ID.
            mime_type: Target MIME type (e.g., 'text/plain', 'application/pdf').
        
        Returns:
            Exported file content as bytes.
        """
        try:
            request = self.service.files().export_media(fileId=file_id, mimeType=mime_type)
            content = request.execute()
            return content
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise