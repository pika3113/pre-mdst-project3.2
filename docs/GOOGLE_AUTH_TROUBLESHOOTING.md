# Google Authentication Troubleshooting Guide

## Error: "Missing required parameter: client_id"

This error typically comes from Google's OAuth service, not your backend. Here's how to fix it:

### 1. Verify Google Cloud Console Setup

#### Check OAuth 2.0 Client Configuration:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** > **Credentials**
4. Find your OAuth 2.0 Client ID: `1088112528465-ro2dcca135u3ha5vocml9sebmiqn52fh.apps.googleusercontent.com`
5. Click on it to edit

#### Verify These Settings:
- **Application type**: Web application
- **Authorized redirect URIs** must include EXACTLY:
  ```
  http://localhost:3000/auth/google/callback
  ```
- **Name**: Any descriptive name

### 2. Check OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**
2. Ensure the consent screen is configured
3. Add your test email to **Test users** if in testing mode
4. Required fields:
   - App name
   - User support email
   - Developer contact information

### 3. Enable Required APIs
Ensure these APIs are enabled:
1. **Google+ API** (deprecated but sometimes needed)
2. **Google OAuth2 API**
3. **People API** (recommended)

### 4. Test the OAuth URL Manually

Copy this URL and test it in your browser:
```
https://accounts.google.com/o/oauth2/auth?client_id=1088112528465-ro2dcca135u3ha5vocml9sebmiqn52fh.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fgoogle%2Fcallback&scope=openid%2Bemail%2Bprofile&response_type=code&access_type=offline
```

### 5. Common Issues and Fixes

#### Issue: "redirect_uri_mismatch"
**Fix**: Ensure exact match in Google Console:
- Add: `http://localhost:3000/auth/google/callback`
- NOT: `http://localhost:3000/auth/google/callback/`
- NOT: `https://localhost:3000/auth/google/callback`

#### Issue: "invalid_client"
**Fix**: 
- Regenerate client secret
- Ensure client ID is from the correct Google project
- Check if OAuth app is suspended

#### Issue: "access_denied"
**Fix**:
- Add your email to test users
- Publish the OAuth consent screen
- Check app verification status

### 6. Alternative OAuth Endpoint

Try updating your Google auth URL to use the v2 endpoint:

In `backend/services/google_auth_service.py`, change:
```python
self.google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
```

### 7. Debug Steps

1. **Check browser console** when clicking "Sign in with Google"
2. **Check network tab** to see the exact request being made
3. **Test OAuth URL directly** in browser
4. **Check Google Cloud Console logs** for any API errors

### 8. Production Considerations

For production deployment:
- Update redirect URI to your domain
- Verify domain ownership in Google Console
- Complete OAuth app verification if needed
- Update CORS settings in your backend

### 9. Environment Variables Check

Verify in your .env file:
```bash
# Current values (update if needed)
GOOGLE_CLIENT_ID=1088112528465-ro2dcca135u3ha5vocml9sebmiqn52fh.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

### 10. Quick Fix Script

Create a new OAuth 2.0 Client ID if the current one is problematic:
1. Delete the existing client ID
2. Create a new one with the same settings
3. Update your .env file with the new credentials
4. Restart your Docker containers

## Need More Help?

If these steps don't resolve the issue:
1. Check the exact error message in browser console
2. Look at the network requests to see what's failing
3. Try creating a completely new Google Cloud project
4. Verify your Google account has proper permissions
