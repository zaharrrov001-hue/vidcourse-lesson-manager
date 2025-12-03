"""Authentication module for Google OAuth and user management."""
import os
import json
from flask import session, redirect, url_for, request
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from config import Config


class User(UserMixin):
    """User class for Flask-Login."""
    
    def __init__(self, user_id, email, name, picture=None):
        self.id = user_id
        self.email = email
        self.name = name
        self.picture = picture
        self.google_credentials = None
        self.getcourse_api_key = None
        self.getcourse_account = None
        self.drive_folder_id = None
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'picture': self.picture,
            'getcourse_api_key': self.getcourse_api_key,
            'getcourse_account': self.getcourse_account,
            'drive_folder_id': self.drive_folder_id
        }
    
    @staticmethod
    def from_dict(data):
        """Create user from dictionary."""
        user = User(
            user_id=data['id'],
            email=data['email'],
            name=data['name'],
            picture=data.get('picture')
        )
        user.getcourse_api_key = data.get('getcourse_api_key')
        user.getcourse_account = data.get('getcourse_account')
        user.drive_folder_id = data.get('drive_folder_id')
        return user


class AuthManager:
    """Manages authentication and user sessions."""
    
    # OAuth 2.0 scopes
    SCOPES = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    def __init__(self, app):
        self.app = app
        # Use /tmp for Vercel (read-only filesystem except /tmp)
        self.users_file = os.getenv('USERS_FILE', '/tmp/users.json' if os.getenv('VERCEL') else 'users.json')
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from file."""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    return {uid: User.from_dict(user_data) for uid, user_data in data.items()}
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Save users to file."""
        try:
            data = {uid: user.to_dict() for uid, user in self.users.items()}
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            # On Vercel, /tmp might not persist, log error but continue
            print(f"Warning: Could not save users file: {e}")
    
    def get_flow(self):
        """Create OAuth flow."""
        client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/auth/callback")]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/auth/callback")
        )
        return flow
    
    def get_user(self, user_id):
        """Get user by ID."""
        return self.users.get(user_id)
    
    def create_or_update_user(self, user_info, credentials):
        """Create or update user from Google OAuth response."""
        user_id = user_info['id']
        email = user_info['email']
        name = user_info.get('name', email)
        picture = user_info.get('picture')
        
        if user_id in self.users:
            user = self.users[user_id]
            user.email = email
            user.name = name
            user.picture = picture
        else:
            user = User(user_id, email, name, picture)
            self.users[user_id] = user
        
        # Store credentials in session (in production, use secure storage)
        session['google_credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        self._save_users()
        return user
    
    def update_user_settings(self, user_id, getcourse_api_key=None, getcourse_account=None, drive_folder_id=None):
        """Update user settings."""
        if user_id in self.users:
            user = self.users[user_id]
            if getcourse_api_key is not None:
                user.getcourse_api_key = getcourse_api_key
            if getcourse_account is not None:
                user.getcourse_account = getcourse_account
            if drive_folder_id is not None:
                user.drive_folder_id = drive_folder_id
            self._save_users()
            return user
        return None