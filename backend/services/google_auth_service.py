import os
import requests
from typing import Optional, Dict
from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import json
from urllib.parse import urlencode, quote_plus

class GoogleOAuthService:
    def __init__(self):
        # Google OAuth configuration
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        
        # Google OAuth URLs
        self.google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        # Redirect URI (this should match what you set in Google Console)
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")
        
        # Scopes we need
        self.scopes = [
            "openid",
            "email",
            "profile"
        ]
    
    def get_authorization_url(self, state: str = None) -> str:
        """Generate Google OAuth authorization URL"""
        if not self.client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth client_id not configured"
            )
            
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),  # Use spaces for scope separation
            "response_type": "code",
            "access_type": "offline",
        }
        
        if state:
            params["state"] = state
        
        # Use proper URL encoding
        param_string = urlencode(params, quote_via=quote_plus)
        return f"{self.google_auth_url}?{param_string}"
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        response = requests.post(self.google_token_url, data=token_data)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token"
            )
        
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict:
        """Get user information from Google using access token"""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.google_userinfo_url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user information from Google"
            )
        
        return response.json()
    
    def verify_id_token(self, id_token_str: str) -> Optional[Dict]:
        """Verify Google ID token and extract user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                self.client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return idinfo
            
        except ValueError as e:
            return None
    
    def process_google_auth(self, code: str) -> Dict:
        """Complete Google OAuth flow and return user info"""
        # Exchange code for tokens
        token_response = self.exchange_code_for_token(code)
        
        # Get user info using access token
        user_info = self.get_user_info(token_response["access_token"])
        
        # Also verify ID token if present
        if "id_token" in token_response:
            id_info = self.verify_id_token(token_response["id_token"])
            if id_info:
                # Merge information from both sources
                user_info.update(id_info)
        
        return {
            "google_id": user_info.get("id"),
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "given_name": user_info.get("given_name"),
            "family_name": user_info.get("family_name"),
            "picture": user_info.get("picture"),
            "verified_email": user_info.get("verified_email", False)
        }
