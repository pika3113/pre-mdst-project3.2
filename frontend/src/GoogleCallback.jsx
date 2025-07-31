import React, { useEffect, useState, useRef } from 'react';
import { API_BASE_URL } from './config';

function GoogleCallback({ onAuthSuccess, onAuthError }) {
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('Processing Google authentication...');
  const hasProcessedRef = useRef(false);

  useEffect(() => {
    console.log('GoogleCallback component mounted');
    console.log('URL params:', window.location.search);
    console.log('hasProcessedRef:', hasProcessedRef.current);
    
    if (hasProcessedRef.current) {
      console.log('Already processed, skipping');
      return;
    }
    
    const handleCallback = async () => {
      // Prevent multiple executions
      if (hasProcessedRef.current) {
        console.log('Google OAuth callback - Already processed, skipping');
        return;
      }
      
      hasProcessedRef.current = true;
      
      try {
        // Get the authorization code from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');

        console.log('Google OAuth callback - URL params:', {
          code: code ? 'present' : 'missing',
          state: state ? 'present' : 'missing',
          error: error,
          fullURL: window.location.href
        });

        if (error) {
          throw new Error(`Google auth error: ${error}`);
        }

        if (!code) {
          throw new Error('No authorization code received from Google');
        }

        setMessage('Exchanging code for tokens...');
        console.log('Google OAuth callback - Sending request to backend...');
        console.log('Sending request to backend with:', { code, state });
        console.log('API_BASE_URL:', API_BASE_URL);

        // Send code to backend
        const response = await fetch(`${API_BASE_URL}/auth/google/callback`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code, state }),
        });

        console.log('Backend response status:', response.status);
        console.log('Backend response ok:', response.ok);

        if (response.ok) {
          const data = await response.json();
          console.log('Backend response data:', data);

          // Store token and user info
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('user', JSON.stringify(data.user));

          setStatus('success');
          setMessage('Authentication successful! Redirecting...');

          console.log('Google OAuth callback - Success! Calling onAuthSuccess...');
          // Call success callback
          setTimeout(() => {
            onAuthSuccess(data.user);
          }, 1000);
        } else {
          const errorText = await response.text();
          console.log('Backend error response:', errorText);
          throw new Error(errorText || 'Authentication failed');
        }

      } catch (error) {
        console.error('Google OAuth callback - Error:', error);
        setStatus('error');
        setMessage(error.message);
        
        setTimeout(() => {
          onAuthError(error.message);
        }, 2000);
      }
    };

    handleCallback();
  }, []); // Empty dependency array to run only once

  return (
    <div className="google-callback">
      <div className="callback-container">
        <div className="callback-icon">
          {status === 'processing' && (
            <div className="spinner"></div>
          )}
          {status === 'success' && (
            <div className="success-icon">✓</div>
          )}
          {status === 'error' && (
            <div className="error-icon">⚠️</div>
          )}
        </div>
        
        <div className="callback-message">
          <h2>Google Authentication</h2>
          <p>{message}</p>
        </div>
      </div>

      <style jsx>{`
        .google-callback {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }

        .callback-container {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(16px);
          border-radius: 20px;
          padding: 3rem;
          text-align: center;
          color: white;
          border: 1px solid rgba(255, 255, 255, 0.1);
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }

        .callback-icon {
          margin-bottom: 1.5rem;
          font-size: 3rem;
        }

        .spinner {
          width: 50px;
          height: 50px;
          border: 3px solid rgba(255, 255, 255, 0.3);
          border-top: 3px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto;
        }

        .success-icon {
          color: #10b981;
          font-size: 4rem;
          font-weight: bold;
        }

        .error-icon {
          color: #ef4444;
          font-size: 4rem;
        }

        .callback-message h2 {
          margin: 0 0 1rem 0;
          font-size: 1.5rem;
        }

        .callback-message p {
          margin: 0;
          opacity: 0.9;
          font-size: 1rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default GoogleCallback;
